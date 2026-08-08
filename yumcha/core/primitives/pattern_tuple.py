"""Bitmask-accelerated sequence container for characters, patterns, and wildcards.

This module provides data structures to optimize fixed-length pattern matching,
alignment, merging, set-like intersections, and filtering via bitwise integer masks.
"""

import unicodedata
from collections.abc import Iterable, Iterator, Sequence
from types import EllipsisType
from typing import Any, Literal, SupportsIndex, TypeVar, overload

from ..utils.bit import iterate_bits
from .pattern import Pattern

type NormForm = Literal["NFC", "NFD", "NFKC", "NFKD"] | None
"""Unicode normalization forms supported by `unicodedata.normalize` or `None` to disable."""

ELLIPSIS = ...
_MAX_CACHED_LEN = 16
_WILDCARDS_CACHE: tuple[Any, ...] = (...,) * _MAX_CACHED_LEN


def _get_wildcard_tuple(length: int) -> tuple[Any, ...]:
    """Retrieves or creates a tuple composed entirely of `Ellipsis` wildcards.

    Uses a pre-allocated cache for lengths up to `_MAX_CACHED_LEN` (16)
    to avoid unnecessary tuple allocations.

    Args:
        length: The desired number of wildcard (`...`) slots.

    Returns:
        A tuple of `Ellipsis` objects with the specified length.
    """
    if length <= _MAX_CACHED_LEN:
        return _WILDCARDS_CACHE[:length]
    return (...,) * length


PatternT_co = TypeVar("PatternT_co", bound=Pattern | str, covariant=True)
PatternT = TypeVar("PatternT", bound=Pattern | str)


class PatternTuple(Sequence[PatternT_co]):
    """A bitmask-accelerated immutable sequence container for characters/patterns and wildcards.

    `PatternTuple` tracks populated string slots versus empty wildcard (`Ellipsis`)
    slots using integer bitmasks (`mask`). This structure optimizes fast matching,
    merging, filtering, and intersection operations across fixed-length pattern sequences.

    Attributes:
        mask (int): A bitmask integer where bit `i` is set (1) if slot `i`
            contains a concrete string value rather than an ellipsis.
        weight (int): The Hamming weight or bit count of `mask`.
        full_mask (int): A precomputed bitmask representing total mask
            where all slots up to length `len(self)` are set to 1.
    """

    __slots__ = ("_data", "full_mask", "mask", "weight")

    _data: tuple[PatternT_co, ...]
    mask: int
    weight: int
    full_mask: int

    def __init__(self, iterable: Iterable[PatternT_co]) -> None:
        """Initializes a PatternTuple from an iterable of strings or Ellipsis wildcards.

        Strings are automatically normalized using NFD (Canonical Decomposition).

        Args:
            iterable: An iterable containing string elements or `...` (Ellipsis).
                Can also be an existing `PatternTuple` instance for fast shallow copying.

        Raises:
            TypeError: If any item in `iterable` is neither a `str` nor `Ellipsis`.
        """
        if type(iterable) is PatternTuple:
            self._data = iterable._data
            self.mask = iterable.mask
            self.weight = iterable.weight
            self.full_mask = iterable.full_mask
            return

        items = []
        mask = 0

        _ellipsis = ELLIPSIS

        for idx, item in enumerate(iterable):
            if type(item) is str:
                items.append(unicodedata.normalize("NFD", item))
                mask |= 1 << idx
            elif item is _ellipsis:
                items.append(item)
            else:
                raise TypeError(f"expected str or ellipsis, got {type(item).__name__}")

        self._data = tuple(items)
        self.mask = mask
        self.weight = mask.bit_count()
        self.full_mask = (1 << len(self._data)) - 1

    def __len__(self) -> int:
        """Returns the total number of slots, including wildcards."""
        return len(self._data)

    @overload
    def __getitem__(self, index: int) -> PatternT_co: ...

    @overload
    def __getitem__(self, index: slice) -> "PatternTuple[PatternT_co]": ...

    def __getitem__(self, index: Any) -> Any:
        """Retrieves an item by integer index or a sub-sequence slice as a new PatternTuple.

        Args:
            index: An integer index or a `slice` object.

        Returns:
            The pattern/wildcard element at the index, or a sliced `PatternTuple` instance.
        """
        result = self._data[index]
        if type(index) is slice:
            s_data = self._data
            data_len = len(s_data)
            start, stop, step = index.indices(data_len)

            slice_len = len(result)
            if slice_len == 0:
                return PatternTuple.wildcards(0)

            if step == 1:
                instance = object.__new__(PatternTuple)
                instance._data = result
                instance.mask = (self.mask >> start) & ((1 << slice_len) - 1)
                instance.weight = instance.mask.bit_count()
                instance.full_mask = (1 << slice_len) - 1
                return instance

            old_mask = self.mask
            new_mask = 0

            for destination_idx, source_idx in enumerate(range(start, stop, step)):
                if (old_mask >> source_idx) & 1:
                    new_mask |= 1 << destination_idx

            instance = object.__new__(PatternTuple)
            instance._data = result
            instance.mask = new_mask
            instance.weight = new_mask.bit_count()
            instance.full_mask = (1 << slice_len) - 1
            return instance

        return result

    def __iter__(self) -> Iterator[PatternT_co]:
        """Returns an iterator over the pattern components."""
        return iter(self._data)

    def __contains__(self, value: object) -> bool:
        """Checks whether a given pattern element or wildcard is present in the sequence."""
        return value in self._data

    def __eq__(self, other: object) -> bool:
        """Checks equality against another PatternTuple or standard sequence."""
        if type(other) is PatternTuple:
            return self._data == other._data
        return self._data == other

    def __hash__(self) -> int:
        """Computes a hash based on the tuple data and mask mask."""
        return hash((self._data, self.mask))

    def __repr__(self) -> str:
        """Returns a string representation suitable for debugging."""
        return f"PatternTuple({self._data})"

    def __sub__(self, other: Iterable[Pattern]) -> "PatternTuple[PatternT_co]":
        """Operator overload for difference (`a - b`)."""
        return self.difference(other)

    def __mul__(self, count: SupportsIndex) -> "PatternTuple[PatternT_co]":
        """Multiplies the PatternTuple sequence.

        Args:
            count: Number of times to repeat the sequence.

        Returns:
            A new `PatternTuple` instance with repeated data.
        """
        raw_tuple = self._data * int(count)

        instance = object.__new__(PatternTuple)
        instance._data = raw_tuple

        new_mask = 0
        if (multiplier := int(count)) > 0:
            bit_shift_distance = len(self._data)

            for segment_idx in range(multiplier):
                shifted_mask = self.mask << (segment_idx * bit_shift_distance)
                new_mask |= shifted_mask

        instance.mask = new_mask
        instance.weight = new_mask.bit_count()
        instance.full_mask = (1 << len(raw_tuple)) - 1
        return instance

    def __and__(self, other: Iterable[Pattern]) -> "PatternTuple[PatternT_co]":
        """Operator overload for intersection (`a & b`)."""
        return self.intersection(other)

    def to_string(self, ignore_ellipsis: bool = False, form: NormForm = "NFC") -> str:
        """Converts the sequence elements into a single joined Unicode string.

        Args:
            ignore_ellipsis: If `True`, skips wildcard slots (`...`) during string construction.
                If `False`, incomplete tuples will raise an error.
            form: Unicode normalization form applied to the final result (e.g., 'NFC', 'NFD').
                Pass `None` to skip normalization.

        Returns:
            The combined and normalized string.

        Raises:
            ValueError: If `ignore_ellipsis` is `False` and the tuple contains wildcards.
        """
        if not ignore_ellipsis and not self.is_complete():
            raise ValueError("cannot convert wildcards to string")

        raw_str = "".join(c for c in self._data if type(c) is str)
        return unicodedata.normalize(form, raw_str) if form else raw_str

    def merge(
        self, other: Iterable[PatternT]
    ) -> "PatternTuple[PatternT_co | PatternT]":
        """Combines two PatternTuple slot-by-slot, filling wildcards from either side.

        Args:
            other: The other pattern sequence to merge into this one.

        Returns:
            A new `PatternTuple` with the union of non-wildcard slots from both sequences.

        Raises:
            ValueError: If `other` is of a different length, or if both tuples contain
                conflicting (non-equal) non-wildcard characters at the same slot position.
        """
        if type(other) is not PatternTuple:
            other = PatternTuple(other)

        s_data = self._data
        o_data = other._data
        s_len = len(s_data)

        if s_len != len(o_data):
            raise ValueError(f"expected length of {s_len}, got {len(o_data)}")

        if self is other or s_data == o_data:
            return self

        s_mask = self.mask
        o_mask = other.mask

        for idx in iterate_bits(s_mask & o_mask):
            if s_data[idx] != o_data[idx]:
                raise ValueError(
                    f"conflicting slot at index {idx}: "
                    f"'{s_data[idx]}' and '{o_data[idx]}'"
                )

        if self.is_complete():
            return self

        if (s_mask & o_mask) == o_mask:
            return self

        if (s_mask & o_mask) == s_mask:
            # If 'other' was just an Iterable (e.g., list/tuple), wrap its data in PatternTuple
            instance = object.__new__(PatternTuple)
            instance._data = tuple(other)  # or other._data if converted earlier
            instance.mask = o_mask
            instance.weight = o_mask.bit_count()
            instance.full_mask = (1 << s_len) - 1
            return instance

        new_items: list[Pattern] = list(s_data)

        for idx in iterate_bits((~s_mask) & o_mask):
            new_items[idx] = o_data[idx]

        new_mask = s_mask | o_mask
        instance = object.__new__(PatternTuple)
        instance._data = tuple(new_items)
        instance.mask = new_mask
        instance.weight = new_mask.bit_count()
        instance.full_mask = (1 << s_len) - 1
        return instance

    def separate(self) -> "set[PatternTuple[PatternT_co]]":
        """Decomposes this pattern tuple into individual single-slot PatternTuple.

        Returns:
            A set of `PatternTuple` instances, each having exactly one populated slot
            from `self` and wildcards in all other positions.
        """
        length = len(self._data)
        separated = set()
        _ellipsis = ELLIPSIS
        s_data = self._data

        for idx, lowest_bit in iterate_bits(self.mask, yield_lowest_bit=True):
            items: list[PatternT_co | EllipsisType] = list(_get_wildcard_tuple(length))
            items[idx] = s_data[idx]

            instance = object.__new__(PatternTuple)
            instance._data = tuple(items)
            instance.mask = lowest_bit
            instance.weight = 1
            instance.full_mask = (1 << length) - 1
            separated.add(instance)

        return separated

    def satisfies(self, other: Iterable[Pattern]) -> bool:
        """Determines if this pattern tuple is compatible with another without conflict.

        Two PatternTuple satisfy each other if all overlapping non-wildcard slots match.

        Args:
            other: The sequence to check against.

        Returns:
            `True` if there are no conflicting slot values, `False` otherwise.

        Raises:
            ValueError: If `other` is of a different length.
        """
        if type(other) is not PatternTuple:
            other = PatternTuple(other)

        s_data = self._data
        o_data = other._data

        if len(s_data) != len(o_data):
            raise ValueError(f"expected length of {len(s_data)}, got {len(o_data)}")

        overlap = self.mask & other.mask

        if not overlap:
            return True

        if s_data == o_data:
            return True

        for idx in iterate_bits(overlap):
            if s_data[idx] != o_data[idx]:
                return False

        return True

    def intersection(self, other: Iterable[Pattern]) -> "PatternTuple[PatternT_co]":
        """Calculates the slot-wise intersection of two PatternTuple.

        Only slots that are populated with identical values in **both** patterns
        are retained in the output; all other slots become wildcards (`...`).

        Args:
            other: The sequence to intersect with.

        Returns:
            A new `PatternTuple` containing matching common values and wildcards elsewhere.

        Raises:
            ValueError: If `other` is of a different length.
        """
        if type(other) is not PatternTuple:
            other = PatternTuple(other)

        s_data = self._data
        o_data = other._data
        data_len = len(s_data)

        if data_len != len(o_data):
            raise ValueError(f"expected length of {data_len}, got {len(o_data)}")

        overlap = self.mask & other.mask

        if not overlap:
            instance = object.__new__(PatternTuple)
            instance._data = _get_wildcard_tuple(data_len)
            instance.mask = 0
            instance.weight = 0
            instance.full_mask = (1 << data_len) - 1
            return instance

        if s_data == o_data:
            return self

        _ellipsis = ELLIPSIS
        new_items: list[Pattern] = list(_get_wildcard_tuple(data_len))
        new_mask = 0

        for idx, lowest_bit in iterate_bits(overlap, yield_lowest_bit=True):
            s_p = s_data[idx]
            if s_p == o_data[idx]:
                new_items[idx] = s_p
                new_mask |= lowest_bit

        instance = object.__new__(PatternTuple)
        instance._data = tuple(new_items)
        instance.mask = new_mask
        instance.weight = new_mask.bit_count()
        instance.full_mask = (1 << data_len) - 1
        return instance

    def difference(self, other: Iterable[Pattern]) -> "PatternTuple[PatternT_co]":
        """Calculates the slot-wise difference (relative complement) between two PatternTuple sequences.

        Removes matching populated slots found in `other` from `self`, replacing those positions
        with wildcards (`...`).

        Args:
            other: The sequence whose populated slots should be removed from `self`.

        Returns:
            A new `PatternTuple` with matching populated slots replaced by wildcards (`...`).

        Raises:
            ValueError: If `other` is of a different length, or if `other` contains a non-wildcard
                value that conflicts with a non-wildcard value in `self` at the same slot.
        """
        if type(other) is not PatternTuple:
            other = PatternTuple(other)

        s_data = self._data
        o_data = other._data
        s_len = len(s_data)

        if s_len != len(o_data):
            raise ValueError(f"expected length of {s_len}, got {len(o_data)}")

        overlap = self.mask & other.mask

        # If there are no overlapping populated slots, subtracting 'other' leaves 'self' unchanged
        if not overlap:
            return self

        # Verify that overlapping slots contain matching values before subtracting
        for idx in iterate_bits(overlap):
            if s_data[idx] != o_data[idx]:
                raise ValueError(
                    f"conflicting slot at index {idx}: "
                    f"'{s_data[idx]}' and '{o_data[idx]}'"
                )

        # The new mask keeps only the slots set in self that were NOT set in other
        new_mask = self.mask & ~other.mask

        if new_mask == self.mask:
            return self

        # Rebuild the _data tuple with wildcards at cleared positions
        new_items: list[Pattern] = list(_get_wildcard_tuple(s_len))
        for idx in iterate_bits(new_mask):
            new_items[idx] = s_data[idx]

        instance = object.__new__(PatternTuple)
        instance._data = tuple(new_items)
        instance.mask = new_mask
        instance.weight = new_mask.bit_count()
        instance.full_mask = self.full_mask
        return instance

    def filter(self, mask: int) -> "PatternTuple[PatternT_co]":
        """Applies a bitmask filter, retaining elements only where bitmask bits are enabled.

        Unset bits in the filter mask cause the corresponding slots to be converted to wildcards.

        Args:
            mask: A bitmask integer specifying which slot indices to keep.

        Returns:
            A new `PatternTuple` retaining elements matching the mask.
        """
        target_mask = mask & self.mask

        if target_mask == self.mask:
            return self

        data = self._data
        data_len = len(data)
        result: list[Pattern] = list(_get_wildcard_tuple(data_len))

        for idx in iterate_bits(target_mask):
            result[idx] = data[idx]

        instance = object.__new__(PatternTuple)
        instance._data = tuple(result)
        instance.mask = target_mask
        instance.weight = target_mask.bit_count()
        instance.full_mask = self.full_mask
        return instance

    def is_complete(self) -> bool:
        """Checks whether all slots in the tuple are populated with non-wildcard items.

        Returns:
            `True` if `mask` equals `full_mask`, `False` if any slot contains `...`.
        """
        return self.mask == self.full_mask

    def to_debug_msg(self) -> str:
        """Formats the tuple elements into an easily readable tuple string for debug outputs.

        Returns:
            A string formatted like `('a', ..., 'b')`.
        """
        _ellipsis = ELLIPSIS
        str_components = ("..." if c is _ellipsis else repr(c) for c in self._data)
        return f"({', '.join(str_components)})"

    @classmethod
    def wildcards(cls, length: int) -> "PatternTuple[PatternT_co]":
        """Creates a PatternTuple instance filled entirely with wildcard (`...`) elements.

        Args:
            length: The length (number of slots) of the wildcard PatternTuple.

        Returns:
            A new `PatternTuple` containing only Ellipsis (`...`) wildcards.
        """
        instance = object.__new__(cls)
        instance._data = _get_wildcard_tuple(length)
        instance.mask = 0
        instance.weight = 0
        instance.full_mask = (1 << length) - 1 if length > 0 else 0
        return instance
