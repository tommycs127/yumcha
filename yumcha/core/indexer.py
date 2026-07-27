from collections.abc import Sequence
from operator import itemgetter

from .models import Pattern, SchemeRowDirective
from .pattern_tuple import PatternTuple

type IndexedEntry = tuple[int, PatternTuple, int]

ELLIPSIS = ...


class Indexer:
    pattern_tuple_length: int
    pattern_tuples_raw: list[PatternTuple]
    pattern_tuples_length: int
    indexed_entries: list[IndexedEntry]
    full_mask: int
    char_masks_dicts: list[dict[Pattern, int]]
    charsets: list[set[str]]

    def __init__(
        self,
        patterns: Sequence[Sequence[Pattern]],
        directions: tuple[SchemeRowDirective, ...],
        allowed_directions: set[SchemeRowDirective],
    ) -> None:
        if not patterns:
            raise ValueError("at least one pattern sequence is required")

        pattern_tuple_length = len(patterns[0])
        pattern_tuples_raw: list[PatternTuple] = []
        indexed_entries: list[IndexedEntry] = []

        for raw_idx, pattern in enumerate(patterns):
            if len(pattern) != pattern_tuple_length:
                raise ValueError(
                    f"expecting length of {pattern_tuple_length}, "
                    f"got {len(pattern)} at index {raw_idx} [{pattern}]"
                )

            pattern_tuple = PatternTuple(pattern)
            pattern_tuples_raw.append(pattern_tuple)
            entry = (raw_idx, pattern_tuple, pattern_tuple.priority)
            indexed_entries.append(entry)

        indexed_entries.sort(key=itemgetter(2), reverse=True)

        pattern_tuples_length = len(pattern_tuples_raw)

        self.pattern_tuple_length = pattern_tuple_length
        self.pattern_tuples_raw = pattern_tuples_raw
        self.pattern_tuples_length = pattern_tuples_length
        self.indexed_entries = indexed_entries
        self.full_mask = (1 << pattern_tuples_length) - 1

        char_masks_dicts = self._index_patterns(
            indexed_entries, directions, allowed_directions
        )

        _ellipsis = ELLIPSIS

        charsets: list[set[str]] = [set(d) - {_ellipsis} for d in char_masks_dicts]  # pyright: ignore[reportAssignmentType]
        self.char_masks_dicts = char_masks_dicts
        self.charsets = charsets

    def find_matches(self, pattern_tuple: PatternTuple) -> list[IndexedEntry]:
        if len(pattern_tuple) != self.pattern_tuple_length:
            raise ValueError(
                f"expecting pattern tuple length of {self.pattern_tuple_length}, "
                f"got {len(pattern_tuple)}"
            )

        match_mask = self.full_mask
        char_masks_dicts = self.char_masks_dicts
        indexed_entries = self.indexed_entries

        for char_idx, char in enumerate(pattern_tuple):
            char_mask = char_masks_dicts[char_idx].get(char, 0)

            match_mask &= char_mask

            if match_mask == 0:
                break

        results: list[IndexedEntry] = []
        mask = match_mask

        while mask:
            lowest_set_bit = mask & -mask
            idx = lowest_set_bit.bit_length() - 1
            results.append(indexed_entries[idx])
            mask &= mask - 1

        return results

    def _index_patterns(
        self,
        pattern_tuples_idx: list[IndexedEntry],
        directions: tuple[SchemeRowDirective, ...],
        allowed_directions: set[SchemeRowDirective],
    ) -> list[dict[Pattern, int]]:
        char_masks_dicts: list[dict[Pattern, int]] = [
            {} for _ in range(self.pattern_tuple_length)
        ]

        for sorted_idx, (raw_idx, pattern_tuple, _) in enumerate(pattern_tuples_idx):
            if directions[raw_idx] not in allowed_directions:
                continue

            bit_position = 1 << sorted_idx

            for char_idx, char in enumerate(pattern_tuple):
                char_masks = char_masks_dicts[char_idx]
                char_masks[char] = char_masks.get(char, 0) | bit_position

        full_mask = self.full_mask

        _ellipsis = ELLIPSIS

        for char_idx, char_masks in enumerate(char_masks_dicts):
            # Extract the wildcard mask if it exists; otherwise, it defaults to 0
            wildcard_mask = char_masks.get(_ellipsis, 0)

            if wildcard_mask == full_mask:
                raise ValueError(f"all patterns contain a wildcard at index {char_idx}")

            # If there are wildcard bits, apply them to all other specific character keys
            if wildcard_mask:
                for char in char_masks:
                    if char is not _ellipsis:
                        char_masks[char] |= wildcard_mask

        return char_masks_dicts


class IntermediateIndexer(Indexer):
    invalid_masks: list[int]

    def build_invalid_masks(self, invalid_patterns: tuple[PatternTuple, ...]) -> None:
        invalid_masks: list[int] = []

        for invalid_pattern in invalid_patterns:
            mask = 0

            for pattern_idx, pattern in enumerate(self.pattern_tuples_raw):
                intersected_pattern = pattern.intersect(invalid_pattern)
                if intersected_pattern.occupancy and pattern.satisfies(invalid_pattern):
                    mask |= 1 << pattern_idx

            invalid_masks.append(mask)

        self.invalid_masks = invalid_masks
