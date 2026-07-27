import unicodedata
from collections.abc import Iterable, Iterator, Sequence
from typing import Any, Literal, SupportsIndex, TypeVar, overload

from .models import Pattern

NormForm = Literal["NFC", "NFD", "NFKC", "NFKD"] | None
ELLIPSIS = ...

P = TypeVar("P", str, Pattern)


class PatternTuple(Sequence[P]):
    __slots__ = ("_data", "full_occupancy", "occupancy", "priority")

    _data: tuple[P, ...]
    occupancy: int
    priority: int
    full_occupancy: int

    def __init__(self, iterable: Iterable[P]):
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
        return len(self._data)

    @overload
    def __getitem__(self, index: int) -> P: ...

    @overload
    def __getitem__(self, index: slice) -> "PatternTuple[P]": ...

    def __getitem__(self, index: Any) -> Any:
        res = self._data[index]
        if isinstance(index, slice):
            return PatternTuple(res)
        return res

    def __iter__(self) -> Iterator[P]:
        return iter(self._data)

    def __contains__(self, value: object) -> bool:
        return value in self._data

    def __eq__(self, other: object) -> bool:
        if type(other) is PatternTuple:
            return self._data == other._data
        return self._data == other

    def __hash__(self) -> int:
        return hash((self._data, self.occupancy))

    def __repr__(self) -> str:
        return f"PatternTuple({self._data})"

    def __mul__(self, count: SupportsIndex) -> "PatternTuple[P]":
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
        if not ignore_ellipsis and not self.is_complete():
            raise ValueError("cannot convert wildcards to string")

        raw_str = "".join(c for c in self._data if type(c) is str)
        return unicodedata.normalize(form, raw_str) if form else raw_str

    def merge(self, other: Iterable[Pattern]) -> "PatternTuple[P]":
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
        return self.occupancy == self.full_occupancy

    def to_debug_msg(self) -> str:
        _ellipsis = ELLIPSIS
        str_components = ("..." if c is _ellipsis else repr(c) for c in self._data)
        return f"({', '.join(str_components)})"
