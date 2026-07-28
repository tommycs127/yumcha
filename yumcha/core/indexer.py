from collections.abc import Sequence
from operator import itemgetter

from .models import Pattern, SchemeRowDirective
from .pattern_tuple import PatternTuple

type IndexedEntry = tuple[int, PatternTuple, int]
"""Type alias for indexed pattern entries: `(original_index, pattern_tuple, priority)`."""

ELLIPSIS = ...


class Indexer:
    """Bitmask-accelerated indexer for fast pattern tuple matching.

    Maps characters per slot index to bitmasks, allowing set intersection operations
    via bitwise `&` across sequence positions to quickly locate matching pattern rules.

    Attributes:
        pattern_tuple_length (int): The required length for all pattern tuples in this indexer.
        pattern_tuples_raw (list[PatternTuple]): The original un-sorted pattern tuples.
        pattern_tuples_length (int): The total count of indexed pattern tuples.
        indexed_entries (list[IndexedEntry]): Entries sorted in descending order of priority.
        full_mask (int): Bitmask integer with all pattern bits enabled (`(1 << count) - 1`).
        char_masks_dicts (list[dict[Pattern, int]]): A list (one per slot position) mapping each
            character/wildcard to its combined match bitmask.
        charsets (list[set[str]]): A list of character sets representing all concrete non-wildcard
            characters accepted at each slot position.
    """

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
        """Initializes and builds the bitmask index from a collection of pattern sequences.

        Args:
            patterns: A sequence of pattern element sequences to index.
            directions: Directives associated with each row in `patterns`.
            allowed_directions: Set of `SchemeRowDirective` directives that determine which
                rows are eligible for inclusion in the index.

        Raises:
            ValueError: If `patterns` is empty, or if any pattern sequence varies in length.
        """
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
        """Finds all candidate entries in the index matching the given input pattern tuple.

        Performs bitwise `AND` across character masks for every slot in `pattern_tuple`,
        iterating set bits to collect matched entries in descending order of priority.

        Args:
            pattern_tuple: The input `PatternTuple` to evaluate against the index.

        Returns:
            A list of matching `IndexedEntry` tuples sorted by priority.

        Raises:
            ValueError: If `pattern_tuple` length does not match `pattern_tuple_length`.
        """
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
        """Constructs bitmask dictionaries for each slot position.

        Args:
            pattern_tuples_idx: Priority-sorted list of indexed entries.
            directions: Row directives corresponding to original raw indices.
            allowed_directions: Set of allowed directives to include.

        Returns:
            A list of dictionaries mapping characters/wildcards to bitmask integers.

        Raises:
            ValueError: If all patterns contain a wildcard at any given slot index.
        """
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
    """An indexer extension supporting validation against invalid pattern masks.

    Attributes:
        invalid_masks (list[int]): A list of bitmasks corresponding to invalid pattern
            rules, where set bits indicate which indexed patterns conflict with a given rule.
    """

    invalid_masks: list[int]

    def build_invalid_masks(self, invalid_patterns: tuple[PatternTuple, ...]) -> None:
        """Precomputes bitmasks indicating which indexed pattern tuples violate invalid rules.

        Args:
            invalid_patterns: A tuple of `PatternTuple` objects defining forbidden feature combinations.
        """
        invalid_masks: list[int] = []

        for invalid_pattern in invalid_patterns:
            mask = 0

            for pattern_idx, pattern in enumerate(self.pattern_tuples_raw):
                intersected_pattern = pattern.intersect(invalid_pattern)
                if intersected_pattern.occupancy and pattern.satisfies(invalid_pattern):
                    mask |= 1 << pattern_idx

            invalid_masks.append(mask)

        self.invalid_masks = invalid_masks
