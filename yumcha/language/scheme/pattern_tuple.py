import unicodedata
from collections.abc import Iterable
from typing import Any


class PatternTuple(tuple):
    def __new__(cls, iterable: Iterable[Any]):
        if isinstance(iterable, PatternTuple):
            return iterable

        items = []
        for item in iterable:
            if isinstance(item, str):
                items.append(unicodedata.normalize("NFD", item))
            elif item is ...:
                items.append(item)
            else:
                raise TypeError(f"expected str or ellipsis, got {type(item).__name__}")

        instance = super().__new__(cls, items)

        occupancy = 0
        for idx, pattern in enumerate(instance):
            if pattern is not ...:
                occupancy |= 1 << idx

        instance.occupancy = occupancy
        return instance

    @property
    def occupancy(self) -> int:
        return self._occupancy

    @occupancy.setter
    def occupancy(self, occupancy: int) -> None:
        if hasattr(self, "_occupancy"):
            raise RuntimeError("occupancy is read-only after initialization")
        self._occupancy = occupancy
