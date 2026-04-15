import re
from functools import cached_property
from types import EllipsisType
from typing import Any

type Pattern = str | EllipsisType
type PatternTuple = tuple[Pattern, ...]
type PatternDict = dict[PatternTuple, PatternTuple]


class PatternMap(dict):
    def _check_and_return(
        self, obj: Any, type_: type[Any], check_content: bool = True
    ) -> Any:
        type_name = type_.__class__.__name__
        if not isinstance(obj, type_):
            raise TypeError(f"not {type_name}")
        if check_content and not obj:
            raise ValueError(f"empty {type_name}")
        return obj

    def __init__(
        self,
        *args,
        key_labels: tuple[str, ...],
        value_labels: tuple[str, ...],
        one_way_map: PatternDict = dict(),
        inverse_map: PatternDict = dict(),
        inversed: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.__key_labels: tuple[str, ...] = self._check_and_return(key_labels, tuple)
        self.__value_labels: tuple[str, ...] = self._check_and_return(
            value_labels, tuple
        )
        self.__one_way_map: PatternDict = self._check_and_return(
            one_way_map, dict, check_content=False
        )
        self.__inverse_map: PatternDict = self._check_and_return(
            inverse_map, dict, check_content=False
        )
        self.__inversed: bool = self._check_and_return(
            inversed, bool, check_content=False
        )
        self.__full_map: PatternDict = self | self.__one_way_map
        self.__rules: list[PatternTuple] = list(self.__full_map.values())

        # Index the tuples

        self.__default_tuple_for_query: PatternTuple = tuple(
            ... for _ in range(len(self.__value_labels))
        )

        self.__rule_index: list[dict[Pattern, set[int]]] = [
            {} for _ in range(len(key_labels))
        ]
        self.__rule_bitmask: list[int] = []

        key_transpose: list[list[str]] = [[] for _ in range(len(key_labels))]

        for idx, key in enumerate(self.__full_map.keys()):
            occupancy = 0
            for key_tuple_item_idx in range(len(key_labels)):
                pattern = key[key_tuple_item_idx]
                if pattern is not ...:
                    occupancy |= 2**key_tuple_item_idx
                    key_transpose[key_tuple_item_idx].append(pattern)
                if pattern not in self.__rule_index[key_tuple_item_idx]:
                    self.__rule_index[key_tuple_item_idx][pattern] = set()
                self.__rule_index[key_tuple_item_idx][pattern].add(idx)
            self.__rule_bitmask.append(occupancy)

        # Build the regex pattern

        self.__key_transpose: list[set[str]] = []
        self.__key_regex_pattern: list[str] = []

        for idx, key_label in enumerate(key_labels):
            key_symbols_set = set(key_transpose[idx])
            self.__key_transpose.append(key_symbols_set)

            sorted_key_symbols_set = sorted(key_symbols_set, key=len, reverse=True)
            columns = "|".join(re.escape(sym) for sym in sorted_key_symbols_set)
            self.__key_regex_pattern.append(f"(?P<{key_label}>{columns})")

        # Lock the object

        self._locked: bool = True

    def __setitem__(self, key, value):
        if hasattr(self, "_locked"):
            raise RuntimeError("FeatureMap object is immutable")
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if key in self.__one_way_map:
            return self.__one_way_map[key]
        return super().__getitem__(key)

    @property
    def rule_index(self) -> list[dict[Pattern, set[int]]]:
        return self.__rule_index

    @property
    def key_labels(self) -> tuple[str, ...]:
        return self.__key_labels

    @property
    def value_labels(self) -> tuple[str, ...]:
        return self.__value_labels

    @property
    def key_transpose(self) -> list[set[str]]:
        return self.__key_transpose

    def is_inversed(self) -> bool:
        return self.__inversed

    def get_by_index(self, index: int) -> PatternTuple:
        return self.__rules[index]

    def _merge_into(self, current: list[Pattern], rule: PatternTuple) -> bool:
        for i, (a, b) in enumerate(zip(current, rule)):
            if a is ...:
                current[i] = b
            elif b is ... or a == b:
                continue
            else:
                return False
        return True

    def _find_best_combination(self, rule_idxs: list[int]) -> PatternTuple | None:
        current = list(self.__default_tuple_for_query)

        for rule_idx in rule_idxs:
            rule = self.__rules[rule_idx]

            snapshot = current[:]
            if not self._merge_into(snapshot, rule):
                continue

            current = snapshot

            if ... not in current:
                return tuple(current)

        return None

    def query(self, query_tuple: PatternTuple) -> PatternTuple:
        if len(query_tuple) != len(self.__key_labels):
            raise ValueError(
                f"expecting tuple length of {len(self.__key_labels)}, "
                f"got {len(query_tuple)}"
            )

        rule_indexes: set[int] = set(_ for _ in range(len(self.__full_map)))

        for idx, pattern in enumerate(query_tuple):
            rule_indexes &= (
                self.__rule_index[idx][pattern] | self.__rule_index[idx][...]
            )

        sorted_rule_indexes: list[int] = sorted(
            rule_indexes,
            # the number of bits is the rule's priority
            key=lambda idx: self.__rule_bitmask[idx].bit_count(),
            reverse=True,
        )

        result_tuple: PatternTuple | None = self._find_best_combination(
            rule_idxs=sorted_rule_indexes
        )

        if result_tuple is None:
            raise ValueError(f"no query result from tuple {query_tuple}")

        return result_tuple

    @cached_property
    def inverse(self) -> "PatternMap":
        if self.__inversed:
            raise AttributeError(
                "inverse is unavailable: this instance is already an inverse"
            )

        inverse = {value: key for key, value in self.items()}

        return PatternMap(
            inverse | self.__inverse_map,
            key_labels=self.__value_labels,
            value_labels=self.__key_labels,
            inversed=True,
        )

    def get_key_regex_pattern(self, label: str) -> str:
        return self.__key_regex_pattern[self.__key_labels.index(label)]
