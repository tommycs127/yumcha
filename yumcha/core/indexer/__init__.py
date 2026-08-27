"""PatternTuple indexing system.

Provides containers to load, index and sort pattern tuples into
positional bitmasks for performant evaluation and lookup.
"""

from __future__ import annotations

from collections.abc import Sequence
from types import MappingProxyType
from typing import TYPE_CHECKING

from ..primitives.pattern_tuple import PatternTuple
from ..utils.collections import SequenceProxy

if TYPE_CHECKING:
    from ..primitives.directives import SchemeDirective
    from ..primitives.pattern import Pattern
    from .models import (
        PatternIndexes,
        PatternIndexesView,
        PatternMasks,
        PatternMasksView,
    )

ELLIPSIS = ...


class Indexer:
    """Manages loading, sorting, bitmask compiling, and index tracking for pattern tuples.

    Pattern tuples are sorted by weight upon registration and indexed using bitmasks
    for each field position to accelerate pattern matching against valid operational directives.
    """

    def __init__(self) -> None:
        """Initializes an empty Indexer container."""
        self._pattern_tuples: list[PatternTuple] = []
        self._pattern_tuples_view: SequenceProxy[PatternTuple] = SequenceProxy(
            self._pattern_tuples
        )
        self._pattern_tuples_frozenset: frozenset[PatternTuple] = frozenset()

        self._directions: list[SchemeDirective] = []
        self._directions_view: SequenceProxy[SchemeDirective] = SequenceProxy(
            self._directions
        )

        self._sorted_indexes: list[int] = []
        self._sorted_indexes_view: SequenceProxy[int] = SequenceProxy(
            self._sorted_indexes
        )

        self._index_ranks: list[int] = []
        self._index_ranks_view: SequenceProxy[int] = SequenceProxy(self._index_ranks)

        self._pattern_masks_by_fields: list[PatternMasksView] = []
        self._pattern_masks_by_fields_view: SequenceProxy[PatternMasksView] = (
            SequenceProxy(self._pattern_masks_by_fields)
        )

        self._charsets: list[frozenset[str]] = []
        self._charsets_view: SequenceProxy[frozenset[str]] = SequenceProxy(
            self._charsets
        )

        self._invalid_pattern_tuples: list[PatternTuple] = []
        self._invalid_pattern_tuples_view: SequenceProxy[PatternTuple] = SequenceProxy(
            self._invalid_pattern_tuples
        )

        self._invalid_pattern_masks: list[int] = []
        self._invalid_pattern_masks_view: SequenceProxy[int] = SequenceProxy(
            self._invalid_pattern_masks
        )

        self._invalid_pattern_masks_indexes_by_fields: list[PatternIndexesView] = []
        self._invalid_pattern_masks_indexes_by_fields_view: SequenceProxy[
            PatternIndexesView
        ] = SequenceProxy(self._invalid_pattern_masks_indexes_by_fields)

    @property
    def pattern_tuples(self) -> SequenceProxy[PatternTuple]:
        """Gets a read-only view of registered pattern tuples.

        Returns:
            SequenceProxy of registered `PatternTuple` instances.
        """
        return self._pattern_tuples_view

    @property
    def pattern_tuples_set(self) -> frozenset[PatternTuple]:
        """Gets a frozenset lookup table of registered pattern tuples.

        Returns:
            Frozenset containing all registered `PatternTuple` instances.
        """
        return self._pattern_tuples_frozenset

    @property
    def directions(self) -> SequenceProxy[SchemeDirective]:
        """Gets a read-only view of directives corresponding to registered pattern tuples.

        Returns:
            SequenceProxy of `SchemeDirective` items aligned with `pattern_tuples`.
        """
        return self._directions_view

    @property
    def sorted_indexes(self) -> SequenceProxy[int]:
        """Gets pattern tuple indices sorted in descending order by weight.

        Returns:
            SequenceProxy of original integer indices ordered by descending weight.
        """
        return self._sorted_indexes_view

    @property
    def index_ranks(self) -> SequenceProxy[int]:
        """Gets the sorted rank position for each original pattern tuple index.

        Returns:
            SequenceProxy of rank integers indexed by original tuple position.
        """
        return self._index_ranks_view

    @property
    def pattern_masks_by_fields(self) -> SequenceProxy[PatternMasksView]:
        """Gets compiled pattern-to-bitmask mappings per field position.

        Returns:
            SequenceProxy of read-only pattern-to-bitmask mappings for each field.
        """
        return self._pattern_masks_by_fields_view

    @property
    def charsets(self) -> SequenceProxy[frozenset[str]]:
        """Gets explicit string character sets present at each field position.

        Returns:
            SequenceProxy of frozensets containing string patterns per field slot.
        """
        return self._charsets_view

    @property
    def invalid_pattern_tuples(self) -> SequenceProxy[PatternTuple]:
        """Gets a read-only view of registered invalid/prohibited pattern tuples.

        Returns:
            SequenceProxy of invalid `PatternTuple` instances used for validation.
        """
        return self._invalid_pattern_tuples_view

    @property
    def invalid_pattern_masks(self) -> SequenceProxy[int]:
        """Gets compiled conflict bitmasks corresponding to invalid pattern tuples.

        Returns:
            SequenceProxy of bitmask integers identifying valid tuples that conflict with invalid rules.
        """
        return self._invalid_pattern_masks_view

    @property
    def invalid_pattern_masks_indexes_by_fields(
        self,
    ) -> SequenceProxy[PatternIndexesView]:
        """Gets field-wise index lookups mapping patterns to invalid tuple array indices.

        Returns:
            SequenceProxy of mappings from pattern tokens to sets of invalid tuple indices.
        """
        return self._invalid_pattern_masks_indexes_by_fields_view

    @property
    def pattern_tuple_length(self) -> int:
        """Gets the fixed slot count (number of fields) across registered pattern tuples.

        Returns:
            Integer length of field slots in registered pattern tuples.

        Raises:
            ValueError: If no pattern tuples are currently loaded.
        """
        if pattern_tuples := self._pattern_tuples:
            return len(pattern_tuples[0])
        raise ValueError("unknown length (no pattern tuples are loaded)")

    def load(
        self,
        pattern_sequences: Sequence[Sequence[Pattern]],
        directions: Sequence[SchemeDirective],
        allowed_directions: set[SchemeDirective],
    ):
        """Loads, sorts, compiles bitmasks, and extracts charsets for pattern sequences.

        Args:
            pattern_sequences: Sequences of pattern elements representing constraint rules.
            directions: Conversion directives corresponding to each pattern sequence.
            allowed_directions: Set of directives permitted during bitmask compilation.

        Raises:
            ValueError: If `pattern_sequences` is empty, lengths mismatch `directions`,
                sequence slot lengths vary, or all sequences contain wildcards at any single position.
        """
        if not pattern_sequences:
            raise ValueError("at least one pattern tuple is required")

        self._reset()
        self._register(pattern_sequences, directions)
        self._sort_and_rank_indexes_by_weight()
        self._compile(allowed_directions)
        self._extract_explicit_charsets()

    def _reset(self) -> None:
        """Clears all compiled pattern data while preserving its read-only views."""
        self._pattern_tuples.clear()
        self._pattern_tuples_frozenset = frozenset()
        self._directions.clear()
        self._sorted_indexes.clear()
        self._index_ranks.clear()
        self._pattern_masks_by_fields.clear()
        self._charsets.clear()
        self._reset_validation_data()

    def _reset_validation_data(self) -> None:
        """Clears all compiled validation and invalid pattern data structures."""
        self._invalid_pattern_tuples.clear()
        self._invalid_pattern_masks.clear()
        self._invalid_pattern_masks_indexes_by_fields.clear()

    def _register(
        self,
        pattern_sequences: Sequence[Sequence[Pattern]],
        directions: Sequence[SchemeDirective],
    ) -> None:
        """Registers pattern tuple sequences.

        Args:
            sequences: Sequences of pattern sequences to register.
            directions: Scheme directives corresponding to each sequence.

        Raises:
            ValueError: If the length of sequences and directions is not the same,
                or if any pattern sequence length differs from the first sequence length.
        """
        if (sequences_length := len(pattern_sequences)) != (
            directions_length := len(directions)
        ):
            raise ValueError(
                f"expecting directions length of {sequences_length}, got {directions_length}"
            )

        expected_pattern_tuple_length = len(pattern_sequences[0])

        pattern_tuples: list[PatternTuple] = []
        append_pattern_tuple = pattern_tuples.append

        for idx, sequence in enumerate(pattern_sequences):
            if len(sequence) != expected_pattern_tuple_length:
                raise ValueError(
                    f"expecting length of {expected_pattern_tuple_length}, "
                    + f"got {len(sequence)} at index {idx} [{sequence!r}]"
                )

            append_pattern_tuple(PatternTuple(sequence))

        self._pattern_tuples[:] = pattern_tuples
        self._pattern_tuples_frozenset = frozenset(pattern_tuples)
        self._directions[:] = directions

    def _sort_and_rank_indexes_by_weight(self) -> None:
        """Sorts pattern tuple indices by weight in descending order and assigns rank positions."""
        pattern_tuples = self._pattern_tuples
        pattern_tuples_length = len(pattern_tuples)

        weighted_indexes = sorted(
            ((pattern_tuples[idx].weight, idx) for idx in range(pattern_tuples_length)),
            key=lambda item: item[0],
            reverse=True,
        )

        sorted_indexes = [item[1] for item in weighted_indexes]
        index_ranks: list[int] = [0] * pattern_tuples_length

        for rank, origin_idx in enumerate(sorted_indexes):
            index_ranks[origin_idx] = rank

        self._sorted_indexes[:] = sorted_indexes
        self._index_ranks[:] = index_ranks

    def _compile(
        self,
        allowed_directions: set[SchemeDirective],
    ) -> None:
        """Compiles field-by-field bitmasks for registered pattern tuples
        matching allowed directions.

        Args:
            allowed_directions: Directives that should be included in bitmask generation.

        Raises:
            ValueError: If every pattern tuple contains a wildcard at the same field index.
        """
        pattern_tuples = self._pattern_tuples
        directions = self._directions
        pattern_tuple_length = len(pattern_tuples[0]) if pattern_tuples else 0

        pattern_masks_by_fields: list[PatternMasks] = [
            {} for _ in range(pattern_tuple_length)
        ]

        for idx, pattern_tuple in enumerate(pattern_tuples):
            if directions[idx] not in allowed_directions:
                continue

            bit = 1 << idx

            for pattern_idx, pattern in enumerate(pattern_tuple):
                pattern_masks = pattern_masks_by_fields[pattern_idx]
                if pattern in pattern_masks:
                    pattern_masks[pattern] |= bit
                else:
                    pattern_masks[pattern] = bit

        full_mask = (1 << len(pattern_tuples)) - 1
        _ellipsis = ELLIPSIS

        for idx, pattern_masks in enumerate(pattern_masks_by_fields):
            if _ellipsis not in pattern_masks:
                continue

            wildcard_mask = pattern_masks[_ellipsis]

            if wildcard_mask == full_mask:
                raise ValueError(
                    f"all pattern tuples contain a wildcard at index {idx}"
                )

            if wildcard_mask:
                for pattern in pattern_masks:
                    if pattern is not _ellipsis:
                        pattern_masks[pattern] |= wildcard_mask

        self._pattern_masks_by_fields[:] = (
            MappingProxyType(pattern_masks) for pattern_masks in pattern_masks_by_fields
        )

    def _extract_explicit_charsets(self) -> None:
        """Extracts frozensets of explicit string patterns present at each field position."""
        self._charsets[:] = (
            frozenset(pattern for pattern in pattern_masks if isinstance(pattern, str))
            for pattern_masks in self._pattern_masks_by_fields
        )

    def load_invalid_patterns(
        self,
        invalid_pattern_sequences: Sequence[Sequence[Pattern]],
    ):
        """Loads, registers, and compiles bitmask filters for invalid pattern sequences.

        Args:
            invalid_pattern_sequences: Sequences of prohibited pattern combinations.

        Raises:
            ValueError: If an invalid tuple contradicts all valid tuples or is already
                registered as a valid pattern tuple.
        """
        self._reset_validation_data()
        self._register_validation_data(invalid_pattern_sequences)
        self._compile_validation_data()

    def _register_validation_data(
        self,
        invalid_pattern_sequences: Sequence[Sequence[Pattern]],
    ) -> None:
        """Registers invalid pattern sequences into `PatternTuple` instances.

        Args:
            invalid_pattern_sequences: Sequences of prohibited pattern combinations to register.
        """
        self._invalid_pattern_tuples[:] = [
            PatternTuple(invalid_pattern_sequence)
            for invalid_pattern_sequence in invalid_pattern_sequences
        ]

    def _compile_validation_data(self) -> None:
        """Compiles conflict bitmasks and field index mappings for invalid pattern tuples.

        Raises:
            ValueError: If an invalid tuple invalidates all registered tuples (full mask conflict)
                or was already registered as a valid pattern tuple.
        """
        pattern_masks_by_fields = self._pattern_masks_by_fields
        pattern_tuples_frozenset = self._pattern_tuples_frozenset
        invalid_pattern_tuples = self._invalid_pattern_tuples

        pattern_tuple_length = self.pattern_tuple_length

        invalid_pattern_masks: list[int] = []
        invalid_pattern_masks_indexes_by_fields: list[PatternIndexes] = [
            {} for _ in range(pattern_tuple_length)
        ]

        full_mask = (1 << len(self._pattern_tuples)) - 1
        _ellipsis = ELLIPSIS

        for idx, invalid_pattern_tuple in enumerate(invalid_pattern_tuples):
            invalid_pattern_mask = full_mask

            for pattern_idx, pattern in enumerate(invalid_pattern_tuple):
                if pattern is _ellipsis:
                    continue

                pattern_masks = pattern_masks_by_fields[pattern_idx]
                if invalid_pattern_mask:
                    if pattern not in pattern_masks:
                        invalid_pattern_mask = 0
                    else:
                        invalid_pattern_mask &= pattern_masks[pattern]

                invalid_pattern_masks_indexes = invalid_pattern_masks_indexes_by_fields[
                    pattern_idx
                ]
                if pattern not in invalid_pattern_masks_indexes:
                    invalid_pattern_masks_indexes[pattern] = {idx}
                else:
                    invalid_pattern_masks_indexes[pattern].add(idx)

            if invalid_pattern_mask == full_mask:
                raise ValueError(
                    f"invalid pattern tuple {invalid_pattern_tuple!r} "
                    + "contradicts all existing pattern tuples"
                )
            elif invalid_pattern_tuple in pattern_tuples_frozenset:
                raise ValueError(
                    f"invalid pattern tuple {invalid_pattern_tuple!r} "
                    + "is already registered as a valid pattern tuple"
                )

            invalid_pattern_masks.append(invalid_pattern_mask)

        self._invalid_pattern_masks[:] = invalid_pattern_masks
        self._invalid_pattern_masks_indexes_by_fields[:] = (
            MappingProxyType({k: frozenset(v) for k, v in field_dict.items()})
            for field_dict in invalid_pattern_masks_indexes_by_fields
        )
