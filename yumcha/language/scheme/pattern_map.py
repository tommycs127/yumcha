from functools import cached_property
from typing import Any

from .pattern_tuple import PatternTuple
from .schema import Pattern, PatternRegistry


class PatternMap(dict):
    def __init__(
        self,
        *args,
        key_tuple_length: int,
        value_tuple_length: int,
        label_indexes_list: list[tuple[int, ...]],
        one_way_map: PatternRegistry = dict(),
        inverse_map: PatternRegistry = dict(),
        inversed: bool = False,
        **kwargs,
    ):
        initial_map = dict(*args, **kwargs)
        converted_map = {
            PatternTuple(key): PatternTuple(value) for key, value in initial_map.items()
        }

        super().__init__(converted_map)

        if key_tuple_length < 1:
            raise ValueError("argument 'key_tuple_length' must be positive integer")
        if value_tuple_length < 1:
            raise ValueError("argument 'value_tuple_length' must be positive integer")

        self.__key_tuple_length = key_tuple_length
        self.__value_tuple_length = value_tuple_length
        self.__label_indexes_list = label_indexes_list

        self.__one_way_map: dict[PatternTuple, PatternTuple] = {
            PatternTuple(key): PatternTuple(value) for key, value in one_way_map.items()
        }
        self.__inverse_map: dict[PatternTuple, PatternTuple] = {
            PatternTuple(key): PatternTuple(value) for key, value in inverse_map.items()
        }

        self.__inversed: bool = inversed
        self.__full_map: dict[PatternTuple, PatternTuple] = self | self.__one_way_map
        self.__rules: list[PatternTuple] = list(self.__full_map.values())

        self.__default_tuple_for_query: PatternTuple = PatternTuple(
            ... for _ in range(value_tuple_length)
        )

        # Compute the transpose of key tuples and check if they match the schema

        self.__keys_transpose_sets: list[set[str]] = [
            set() for _ in range(key_tuple_length)
        ]
        self.__rule_index: list[dict[Pattern, set[int]]] = [
            dict() for _ in range(key_tuple_length)
        ]
        self.__rule_bitmask: list[int] = []

        for idx, (key, value) in enumerate(self.__full_map.items()):
            self.__rule_bitmask.append(key.occupancy)

            str_indexes = set()

            try:
                for key_idx, (transpose_set, key_pattern) in enumerate(
                    zip(self.__keys_transpose_sets, key, strict=True)
                ):
                    if isinstance(key_pattern, str):
                        str_indexes.update(label_indexes_list[key_idx])
                        transpose_set.add(key_pattern)
                    self.__rule_index[key_idx].setdefault(key_pattern, set()).add(idx)
            except (ValueError, TypeError) as e:
                raise ValueError(f"invalid key {key}: {e}") from e

            try:
                for value_idx, value_pattern in enumerate(value):
                    is_str = isinstance(value_pattern, str)
                    is_ellipsis = value_pattern is ...

                    if is_str and value_idx not in str_indexes:
                        raise TypeError(
                            f"expected ellipsis "
                            f"at index {value_idx}, "
                            f"got {type(value_pattern).__name__}"
                        )

                    if is_ellipsis and value_idx in str_indexes:
                        raise TypeError(
                            f"expected str "
                            f"at index {value_idx}, "
                            f"got {type(value_pattern).__name__}"
                        )

                    if not (is_str or is_ellipsis):
                        raise TypeError(
                            "expected str or ellipsis, "
                            f"got {type(value_pattern).__name__}"
                        )
            except TypeError as e:
                raise ValueError(f"invalid value {value}: {e}") from e

        # Lock the object

        self._locked: bool = True

    def _lock_check(self):
        if hasattr(self, "_locked"):
            raise RuntimeError(f"{self.__class__.__name__} object is immutable")

    def __setitem__(self, key, value):
        self._lock_check()
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if key in self.__one_way_map:
            return self.__one_way_map[key]
        return super().__getitem__(key)

    def __delitem__(self, key: Any) -> None:
        self._lock_check()
        super().__delitem__(key)

    def update(self, *args, **kwargs) -> None:
        self._lock_check()
        super().update(*args, **kwargs)

    def pop(self, key: Any, default: Any = None) -> Any:
        self._lock_check()
        return super().pop(key, default)

    def popitem(self) -> tuple[Any, Any]:
        self._lock_check()
        return super().popitem()

    def clear(self) -> None:
        self._lock_check()
        super().clear()

    def setdefault(self, key: Any, default: Any = None) -> Any:
        if key not in self:
            self._lock_check()
        return super().setdefault(key, default)

    @property
    def rule_index(self) -> list[dict[Pattern, set[int]]]:
        return self.__rule_index

    @property
    def key_tuple_length(self) -> int:
        return self.__key_tuple_length

    @property
    def value_tuple_length(self) -> int:
        return self.__value_tuple_length

    @property
    def keys_transpose_set(self) -> list[set[str]]:
        return self.__keys_transpose_sets

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
                return PatternTuple(current)

        return None

    def query(self, query_tuple: PatternTuple) -> PatternTuple:
        if len(query_tuple) != self.__key_tuple_length:
            raise ValueError(
                f"expected tuple length of {self.__key_tuple_length}, "
                f"got {len(query_tuple)}"
            )

        rule_indexes: set[int] = set(range(len(self.__full_map)))

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
    def inverse_label_indexes_list(self) -> list[tuple[int, ...]]:
        all_indexes = [i for t in self.__label_indexes_list for i in t]

        if not all_indexes:
            return []

        max_idx = max(all_indexes)
        full_range = range(max_idx + 1)

        all_indexes_set = set(all_indexes)
        expected_indexes_set = set(full_range)

        if all_indexes_set != expected_indexes_set:
            raise ValueError(
                "the integers provided do not form a complete sequence. "
                f"Missing {expected_indexes_set - all_indexes_set}"
            )

        inverse = [[] for _ in full_range]

        for value, target_indexes in enumerate(self.__label_indexes_list):
            for target_index in target_indexes:
                inverse[target_index].append(value)

        return [tuple(item) for item in inverse]

    @cached_property
    def inverse(self) -> "PatternMap":
        if self.__inversed:
            raise AttributeError(
                "inverse is unavailable: this instance is already an inverse"
            )

        inversed_map = {value: key for key, value in self.items()}

        return PatternMap(
            inversed_map | self.__inverse_map,
            key_tuple_length=self.__value_tuple_length,
            value_tuple_length=self.__key_tuple_length,
            label_indexes_list=self.inverse_label_indexes_list,
            inversed=True,
        )

    def get_key_transpose_set(self, key_label_index: int) -> set[str]:
        return self.__keys_transpose_sets[key_label_index]
