import re
from collections.abc import Iterable
from functools import cached_property
from types import EllipsisType
from typing import Any

from .types import FeatureTuple


class FeatureMap(dict):
    def __init__(self, *args, **kwargs):
        key_labels = kwargs.pop("key_labels", tuple())
        value_labels = kwargs.pop("value_labels", tuple())
        inversed = kwargs.pop("inversed", False)
        inverse_map = kwargs.pop("inverse_map", dict())

        super().__init__(*args, **kwargs)

        if not self:
            raise ValueError("empty dict")

        def _fail_length(target: FeatureTuple, expected: tuple[int, ...]):
            exp_str = ", ".join(map(str, expected))
            raise ValueError(
                f"inconsistent tuple length: {target}. Expected {exp_str}, got {len(target)}"
            )

        def _tuple_items_match_type(t: tuple[Any], types: tuple[type, ...]):
            if not all(isinstance(x, types) for x in t):
                _fail_item_type()

        def _fail_item_type():
            raise TypeError("items of tuple must be either str or EllipsisType")

        if not isinstance(key_labels, tuple):
            raise TypeError("key_labels is not tuple")
        if not isinstance(value_labels, tuple):
            raise TypeError("value_labels is not tuple")

        self.__key_arity = len(key_labels)
        self.__value_arity = len(value_labels)

        if self.__key_arity == 0:
            raise ValueError("key tuple cannot be empty")
        if self.__value_arity == 0:
            raise ValueError("value tuple cannot be empty")

        value_tuple_reqs = (self.__value_arity, self.__value_arity + 1)

        self.__key_labels = key_labels
        self.__value_labels = value_labels

        for k, v in list(self.items()):
            if not isinstance(k, tuple):
                raise TypeError(f"key '{k}' is not tuple")
            elif not isinstance(v, tuple):
                raise TypeError(f"value '{v}' is not tuple")

            if len(k) != self.__key_arity:
                _fail_length(k, (self.__key_arity,))

            _tuple_items_match_type(k, (str, EllipsisType))

            if len(v) not in value_tuple_reqs:
                _fail_length(v, value_tuple_reqs)

            if len(v) == value_tuple_reqs[0]:
                _tuple_items_match_type(v, (str, EllipsisType))
                self[k] = (*v, True)
            elif len(v) == value_tuple_reqs[1]:
                if not isinstance(v[-1], bool):
                    raise TypeError(f"the extra item of value tuple {v} is not bool")
            else:
                _fail_length(v, value_tuple_reqs)

        self._locked = True
        self.__inversed = inversed
        self.__inverse_map = inverse_map

    def __setitem__(self, key, value):
        if hasattr(self, "_locked"):
            raise RuntimeError("FeatureMap object is immutable")
        super().__setitem__(key, value)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return value[:-1]

    @property
    def key_arity(self) -> int:
        return self.__key_arity

    @property
    def value_arity(self) -> int:
        return self.__value_arity

    def is_inversed(self) -> bool:
        return self.__inversed

    def __build_inverse(
        self,
        key_labels: tuple[str, ...],
        value_labels: tuple[str, ...],
        inversed: bool = False,
    ) -> "FeatureMap":
        inverse = {}

        for k, v in self.items():
            if not v[-1]:
                continue
            elif v[:-1] in inverse:
                tuple_before_str = str(v[:-1])
                tuple_before_str = tuple_before_str.replace("Ellipsis", "...")
                tuple_after_str = str((*v[:-1], False))
                tuple_after_str = tuple_after_str.replace("Ellipsis", "...")
                raise ValueError(
                    "duplicated value. "
                    "Add False at the end of the non-mappable tuple(s), "
                    f"i.e. {tuple_before_str} to be {tuple_after_str}"
                )
            inverse[v[:-1]] = k

        return FeatureMap(
            inverse | self.__inverse_map,
            key_labels=key_labels,
            value_labels=value_labels,
            inversed=inversed,
        )

    @cached_property
    def inverse(self) -> "FeatureMap":
        if self.__inversed:
            raise AttributeError(
                "inverse is unavailable: this instance is already an inverse"
            )

        return self.__build_inverse(
            key_labels=self.__value_labels,
            value_labels=self.__key_labels,
            inversed=True,
        )

    @property
    def key_labels(self):
        return self.__key_labels

    @key_labels.setter
    def key_labels(self, labels: tuple[str, ...]) -> None:
        if len(labels) != self.__key_arity:
            raise ValueError(
                "number of names does not match the arity. "
                f"Expected {self.__key_arity}, got {len(labels)}"
            )
        elif any(not isinstance(name, str) for name in labels):
            raise TypeError("must be a string tuple")

        self.__key_labels: tuple[str, ...] = labels

    @property
    def value_labels(self):
        return self.__value_labels

    @value_labels.setter
    def value_labels(self, labels: tuple[str, ...]) -> None:
        if len(labels) != self.__value_arity:
            raise ValueError(
                "number of names does not match the arity. "
                f"Expected {self.__value_arity}, got {len(labels)}"
            )
        elif any(not isinstance(name, str) for name in labels):
            raise TypeError("must be a string tuple")

        self.__value_labels: tuple[str, ...] = labels

    def _get_columns(self, iter: Iterable, axis: int) -> list[str]:
        return [item[axis] for item in iter if item[axis] is not ...]

    def get_key_columns(self, axis: int) -> list[str]:
        return self._get_columns(self.keys(), axis)

    def get_key_columns_by_label(self, label: str) -> list[str]:
        return self.get_key_columns(self.__key_labels.index(label))

    def get_key_regex_pattern(self, label: str) -> str:
        index = self.__key_labels.index(label)
        symbols = set(re.escape(sym) for sym in self.get_key_columns(index))
        columns = "|".join(sorted(symbols, key=len, reverse=True))
        return f"(?P<{label}>{columns})"

    def get_value_columns(self, axis: int) -> list[str]:
        return self._get_columns(self.values(), axis)

    def get_value_columns_by_label(self, label: str) -> list[str]:
        return self.get_value_columns(self.__value_labels.index(label))
