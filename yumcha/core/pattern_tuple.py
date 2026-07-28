import unicodedata
from collections.abc import Iterable, Iterator, Sequence
from typing import Any, Literal, SupportsIndex, TypeVar, overload

from .models import Pattern

NormForm = Literal["NFC", "NFD", "NFKC", "NFKD"] | None
ELLIPSIS = ...

P = TypeVar("P", str, Pattern)


class PatternTuple(Sequence[P]):
    """A bitmask-accelerated immutable sequence container for characters/patterns and wildcards.

    `PatternTuple` tracks populated string slots versus empty wildcard (`Ellipsis`)
    slots using integer bitmasks (`occupancy`). This structure optimizes fast matching,
    merging, filtering, and intersection operations across fixed-length pattern sequences.

    Attributes:
        occupancy (int): A bitmask integer where bit `i` is set (1) if slot `i`
            contains a concrete string value rather than an ellipsis.
        priority (int): The count of populated slots (the Hamming weight or bit count
            of `occupancy`).
        full_occupancy (int): A precomputed bitmask representing total occupancy
            where all slots up to length `len(self)` are set to 1.
    """

    __slots__ = ("_data", "full_occupancy", "occupancy", "priority")

    _data: tuple[P, ...]
    occupancy: int
    priority: int
    full_occupancy: int

    def __init__(self, iterable: Iterable[P]):
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
            self.occupancy = iterable.occupancy
            self.priority = iterable.priority
            self.full_occupancy = iterable.full_occupancy
            return

        items = []
        occupancy = 0

        _ellipsis = ELLIPSIS

        for idx, item in enumerate(iterable):
            if type(item) is str:
                items.append(unicodedata.normalize("NFD", item))
                occupancy |= 1 << idx
            elif item is _ellipsis:
                items.append(item)
            else:
                raise TypeError(f"expected str or ellipsis, got {type(item).__name__}")

        self._data = tuple(items)
        self.occupancy = occupancy
        self.priority = occupancy.bit_count()
        self.full_occupancy = (1 << len(self._data)) - 1

    def __len__(self) -> int:
        """Returns the total number of slots, including wildcards."""
        return len(self._data)

    @overload
    def __getitem__(self, index: int) -> P: ...

    @overload
    def __getitem__(self, index: slice) -> "PatternTuple[P]": ...

    def __getitem__(self, index: Any) -> Any:
        """Retrieves an item by integer index or a sub-sequence slice as a new PatternTuple."""
        res = self._data[index]
        if isinstance(index, slice):
            return PatternTuple(res)
        return res

    def __iter__(self) -> Iterator[P]:
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
        """Computes a hash based on the tuple data and occupancy mask."""
        return hash((self._data, self.occupancy))

    def __repr__(self) -> str:
        """Returns a string representation suitable for debugging."""
        return f"PatternTuple({self._data})"

    def __mul__(self, count: SupportsIndex) -> "PatternTuple[P]":
        """Multiplies the pattern tuple sequence.

        Args:
            count: Number of times to repeat the sequence.

        Returns:
            A new `PatternTuple` instance with repeated data.
        """
        raw_tuple = self._data * int(count)

        instance = object.__new__(PatternTuple)
        instance._data = raw_tuple

        new_occupancy = 0
        if (multiplier := int(count)) > 0:
            bit_shift_distance = len(self._data)

            for segment_idx in range(multiplier):
                shifted_mask = self.occupancy << (segment_idx * bit_shift_distance)
                new_occupancy |= shifted_mask

        instance.occupancy = new_occupancy
        instance.priority = new_occupancy.bit_count()
        instance.full_occupancy = (1 << len(raw_tuple)) - 1
        return instance

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

    def merge(self, other: Iterable[Pattern]) -> "PatternTuple[P]":
        """Combines two pattern tuples slot-by-slot, filling wildcards from either side.

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

        if len(s_data) != len(o_data):
            raise ValueError(f"expected length of {len(s_data)}, got {len(o_data)}")

        if overlap := (self.occupancy & other.occupancy) and s_data != o_data:
            temp_overlap = overlap

            while temp_overlap:
                lowest_bit = temp_overlap & -temp_overlap
                idx = lowest_bit.bit_length() - 1

                if (s_data_i := s_data[idx]) != (o_data_i := o_data[idx]):
                    raise ValueError(
                        f"conflicting slot at index {idx}: "
                        f"'{s_data_i}' and '{o_data_i}'"
                    )

                temp_overlap ^= lowest_bit

        _ellipsis = ELLIPSIS
        s_data_len = len(s_data)

        new_items = [
            s_data[idx] if s_data[idx] is not _ellipsis else o_data[idx]
            for idx in range(s_data_len)
        ]

        instance = object.__new__(PatternTuple)
        instance._data = tuple(new_items)
        instance.occupancy = self.occupancy | other.occupancy
        instance.priority = instance.occupancy.bit_count()
        instance.full_occupancy = (1 << len(new_items)) - 1
        return instance

    def separate(self) -> "set[PatternTuple[P]]":
        """Decomposes this pattern tuple into individual single-slot pattern tuples.

        Returns:
            A set of `PatternTuple` instances, each having exactly one populated slot
            from `self` and wildcards in all other positions.
        """
        length = len(self._data)
        wildcards = (...,) * length
        separated = set()

        _ellipsis = ELLIPSIS

        for idx, pattern in enumerate(self._data):
            if pattern is _ellipsis:
                continue

            t = wildcards[:idx] + (pattern,) + wildcards[idx + 1 :]

            instance = object.__new__(PatternTuple)
            instance._data = t
            instance.occupancy = 1 << idx
            instance.priority = 1
            instance.full_occupancy = (1 << length) - 1
            separated.add(instance)

        return separated

    def satisfies(self, other: Iterable[Pattern]) -> bool:
        """Determines if this pattern tuple is compatible with another without conflict.

        Two pattern tuples satisfy each other if all overlapping non-wildcard slots match.

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

        overlap = self.occupancy & other.occupancy

        if not overlap:
            return True

        if s_data == o_data:
            return True

        temp_overlap = overlap

        while temp_overlap:
            lowest_bit = temp_overlap & -temp_overlap
            idx = lowest_bit.bit_length() - 1

            if s_data[idx] != o_data[idx]:
                return False

            temp_overlap ^= lowest_bit

        return True

    def intersect(self, other: Iterable[Pattern]) -> "PatternTuple[P]":
        """Calculates the slot-wise intersection of two pattern tuples.

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

        if len(self._data) != len(other._data):
            raise ValueError(
                f"expected length of {len(self._data)}, got {len(other._data)}"
            )

        overlap = self.occupancy & other.occupancy
        s_data = self._data
        o_data = other._data
        data_len = len(s_data)

        if not overlap:
            instance = object.__new__(PatternTuple)
            instance._data = (...,) * data_len
            instance.occupancy = 0
            instance.priority = 0
            instance.full_occupancy = (1 << data_len) - 1
            return instance

        _ellipsis = ELLIPSIS
        new_items = []
        new_occupancy = 0

        for idx in range(data_len):
            s_p = s_data[idx]
            if (overlap & (1 << idx)) and s_p == o_data[idx]:
                new_items.append(s_p)
                new_occupancy |= 1 << idx
            else:
                new_items.append(_ellipsis)

        instance = object.__new__(PatternTuple)
        instance._data = tuple(new_items)
        instance.occupancy = new_occupancy
        instance.priority = new_occupancy.bit_count()
        instance.full_occupancy = (1 << len(new_items)) - 1
        return instance

    def filter(self, occupancy: int) -> "PatternTuple[P]":
        """Applies a bitmask filter, retaining elements only where bitmask bits are enabled.

        Unset bits in the filter mask cause the corresponding slots to be converted to wildcards.

        Args:
            occupancy: A bitmask integer specifying which slot indices to keep.

        Returns:
            A new `PatternTuple` retaining elements matching the mask.
        """
        data = self._data
        data_len = len(data)
        target_occupancy = occupancy & self.full_occupancy

        _ellipsis = ELLIPSIS

        result = [
            data[idx] if (occupancy & (1 << idx)) else _ellipsis
            for idx in range(data_len)
        ]

        instance = object.__new__(PatternTuple)
        instance._data = tuple(result)
        instance.occupancy = target_occupancy
        instance.priority = target_occupancy.bit_count()
        instance.full_occupancy = self.full_occupancy
        return instance

    def is_complete(self) -> bool:
        """Checks whether all slots in the tuple are populated with non-wildcard items.

        Returns:
            `True` if `occupancy` equals `full_occupancy`, `False` if any slot contains `...`.
        """
        return self.occupancy == self.full_occupancy

    def to_debug_msg(self) -> str:
        """Formats the tuple elements into an easily readable tuple string for debug outputs.

        Returns:
            A string formatted like `('a', ..., 'b')`.
        """
        _ellipsis = ELLIPSIS
        str_components = ("..." if c is _ellipsis else repr(c) for c in self._data)
        return f"({', '.join(str_components)})"
