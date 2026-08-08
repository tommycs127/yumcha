"""PatternTuple registration and bitmask compilation system.

Provides containers to load, sort, index, and compile pattern tuples into
positional bitmasks for performant evaluation and lookup.
"""

from collections.abc import Sequence
from operator import itemgetter
from types import MappingProxyType
from typing import TYPE_CHECKING

from ..primitives.directives import SchemeDirective
from ..primitives.pattern import Pattern
from ..primitives.pattern_tuple import PatternTuple
from ..utils.collections import SequenceProxy
from .models import PatternMasksView, RegisteredPatternTuple

if TYPE_CHECKING:
    from .models import PatternMasks

ELLIPSIS = ...


class RegisteredPatternTuples:
    """Manages loading, sorting, bitmask compiling, and index tracking for pattern tuples.

    Pattern_tuples are sorted by weight upon registration and indexed using bitmasks for each field position
    to accelerate pattern matching against valid operational directives.
    """

    def __init__(self) -> None:
        """Initializes an empty RegisteredPatternTuples container."""
        self._registrants: list[RegisteredPatternTuple] = []
        self._registrants_view: SequenceProxy[RegisteredPatternTuple] = SequenceProxy(
            self._registrants
        )
        self._pattern_masks_by_fields: list[PatternMasksView] = []
        self._pattern_masks_by_fields_view: SequenceProxy[PatternMasksView] = (
            SequenceProxy(self._pattern_masks_by_fields)
        )
        self._charsets: list[frozenset[str]] = []
        self._charsets_view: SequenceProxy[frozenset[str]] = SequenceProxy(
            self._charsets
        )
        self._moved_indexes: list[int] = []
        self._moved_indexes_view: SequenceProxy[int] = SequenceProxy(
            self._moved_indexes
        )

    @property
    def registrants(self) -> SequenceProxy[RegisteredPatternTuple]:
        """SequenceProxy[RegisteredPatternTuple]: Read-only view of registered pattern tuples sorted by weight."""
        return self._registrants_view

    @property
    def pattern_masks_by_fields(self) -> SequenceProxy[PatternMasksView]:
        """SequenceProxy[PatternMasksView]: Read-only view of per-field pattern bitmask lookup tables."""
        return self._pattern_masks_by_fields_view

    @property
    def charsets(self) -> SequenceProxy[frozenset[str]]:
        """SequenceProxy[frozenset[str]]: Read-only view of explicit character sets found per field index."""
        return self._charsets_view

    @property
    def moved_indexes(self) -> SequenceProxy[int]:
        """SequenceProxy[int]: Read-only view mapping original input indices to sorted registrant indices."""
        return self._moved_indexes_view

    def registrant_by_origin_index(self, source_idx: int) -> RegisteredPatternTuple:
        """Retrieves a registered pattern tuple using its original pre-sort index.

        Args:
            source_idx: The original input index of the pattern tuple.

        Returns:
            The `RegisteredPatternTuple` corresponding to the original index.
        """
        registrant_idx = self._moved_indexes[source_idx]
        return self._registrants[registrant_idx]

    def load(
        self,
        pattern_tuples: Sequence[Sequence[Pattern]],
        directions: Sequence[SchemeDirective],
        allowed_directions: set[SchemeDirective],
    ):
        """Loads, registers, compiles bitmasks, and indexes a set of pattern sequences.

        Args:
            pattern_tuples: Sequences of pattern sequences representing constraint rules.
            directions: Directives corresponding to each pattern sequence.
            allowed_directions: Set of directives permitted during bitmask compilation.

        Raises:
            ValueError: If `pattern_tuples` is empty, if sequences vary in length, or if all
                pattern_tuples contain wildcards at any single position.
        """
        if not pattern_tuples:
            raise ValueError("at least one pattern tuple is required")

        self._register(pattern_tuples, directions)
        self._compile(allowed_directions)
        self._extract_explicit_charsets()
        self._index()

    def _register(
        self,
        sequences: Sequence[Sequence[Pattern]],
        directions: Sequence[SchemeDirective],
    ) -> None:
        """Registers and sorts pattern tuple sequences by weight in descending order.

        Args:
            sequences: Sequences of pattern sequences to register.
            directions: Scheme directives corresponding to each sequence.

        Raises:
            ValueError: If any pattern sequence length differs from the first sequence length.
        """
        expected_pattern_tuple_len = len(sequences[0])
        registrants = self._registrants

        for idx, sequence in enumerate(sequences):
            if (pattern_tuple_len := len(sequence)) != expected_pattern_tuple_len:
                raise ValueError(
                    f"expecting length of {expected_pattern_tuple_len}, "
                    f"got {pattern_tuple_len} at index {idx} [{sequence!r}]"
                )

            pattern_tuple = PatternTuple(sequence)
            direction = directions[idx]
            registrant = RegisteredPatternTuple(
                idx, pattern_tuple, direction, pattern_tuple.weight
            )
            registrants.append(registrant)

        registrants.sort(key=itemgetter(3), reverse=True)

    def _compile(
        self,
        allowed_directions: set[SchemeDirective],
    ) -> None:
        """Compiles field-by-field bitmasks for registered pattern tuples matching allowed directions.

        Args:
            allowed_directions: Directives that should be included in bitmask generation.

        Raises:
            ValueError: If every pattern tuple contains a wildcard at the same field index.
        """
        registrants = self._registrants
        first_pattern_tuple = registrants[0][1]
        pattern_tuple_length = len(first_pattern_tuple)
        pattern_masks_dicts: list[PatternMasks] = [
            {} for _ in range(pattern_tuple_length)
        ]

        for idx, (_, pattern_tuple, direction, _) in enumerate(registrants):
            if direction not in allowed_directions:
                continue

            bit_position = 1 << idx

            for pattern_idx, pattern in enumerate(pattern_tuple):
                pattern_masks = pattern_masks_dicts[pattern_idx]
                pattern_masks[pattern] = pattern_masks.get(pattern, 0) | bit_position

        full_registrants_mask = (1 << len(registrants)) - 1
        _ellipsis = ELLIPSIS

        for idx, pattern_masks in enumerate(pattern_masks_dicts):
            wildcard_mask = pattern_masks.get(_ellipsis, 0)

            if wildcard_mask == full_registrants_mask:
                raise ValueError(
                    f"all pattern tuples contain a wildcard at index {idx}"
                )

            if wildcard_mask:
                for pattern in pattern_masks:
                    if pattern is not _ellipsis:
                        pattern_masks[pattern] |= wildcard_mask

        self._pattern_masks_by_fields[:] = [
            MappingProxyType(pattern_masks) for pattern_masks in pattern_masks_dicts
        ]

    def _extract_explicit_charsets(self) -> None:
        """Extracts frozensets of explicit string patterns present at each field position."""
        _ellipsis = ELLIPSIS
        self._charsets[:] = [
            frozenset(pattern for pattern in pattern_masks if isinstance(pattern, str))
            for pattern_masks in self._pattern_masks_by_fields
        ]

    def _index(self) -> None:
        """Builds an index mapping original sequence indices to sorted registrant indices."""
        registrants = self._registrants
        source_indexes = [-1] * len(registrants)

        for idx, (origin_idx, _, _, _) in enumerate(registrants):
            source_indexes[origin_idx] = idx

        self._moved_indexes[:] = source_indexes


class RegisteredPatternTupleWithInvalidMasks(RegisteredPatternTuples):
    """Extends `RegisteredPatternTuples` with functionality to construct invalid pattern tuple bitmasks.

    Tracks bitmasks representing invalid pattern tuple sets referenced either by origin or
    sorted registrant positions.
    """

    def __init__(self):
        """Initializes RegisteredPatternTupleWithInvalidMasks with empty invalid mask views."""
        super().__init__()

        self._invalid_origin_masks: list[int] = []
        self._invalid_origin_masks_view: SequenceProxy[int] = SequenceProxy(
            self._invalid_origin_masks
        )
        self._invalid_registrant_masks: list[int] = []
        self._invalid_registrant_masks_view: SequenceProxy[int] = SequenceProxy(
            self._invalid_registrant_masks
        )

    @property
    def invalid_origin_masks(self) -> SequenceProxy[int]:
        """SequenceProxy[int]: Read-only view of bitmasks representing invalid pattern tuples keyed by origin index."""
        return self._invalid_origin_masks_view

    @property
    def invalid_registrant_masks(self) -> SequenceProxy[int]:
        """SequenceProxy[int]: Read-only view of bitmasks representing invalid pattern tuples keyed by registrant index."""
        return self._invalid_registrant_masks_view

    def load(
        self,
        pattern_tuples: Sequence[Sequence[Pattern]],
        directions: Sequence[SchemeDirective],
        allowed_directions: set[SchemeDirective],
    ) -> None:
        """Clears stale invalid registrant masks and loads pattern_tuples.

        Args:
            pattern_tuples: Sequences of pattern sequences representing constraint rules.
            directions: Directives corresponding to each pattern sequence.
            allowed_directions: Set of directives permitted during bitmask compilation.
        """
        self._invalid_registrant_masks.clear()
        super().load(pattern_tuples, directions, allowed_directions)

    def build_invalid_masks(
        self,
        invalid_pattern_tuples: Sequence[PatternTuple[Pattern]],
    ) -> None:
        """Computes bitmasks indicating registered pattern tuples satisfied by provided invalid pattern tuples.

        Args:
            invalid_pattern_tuples: A sequence of invalid pattern tuple rules to match against registrants.
        """
        registrants = self._registrants
        invalid_origin_masks: list[int] = []
        invalid_registrant_masks: list[int] = []

        indexed_pattern_tuples = [
            (1 << idx, 1 << registrant[0], registrant[1])
            for idx, registrant in enumerate(registrants)
        ]

        for invalid_pattern_tuple in invalid_pattern_tuples:
            origin_mask = 0
            registrant_mask = 0

            for registrant_bit, origin_bit, pattern_tuple in indexed_pattern_tuples:
                if pattern_tuple.satisfies(invalid_pattern_tuple):
                    origin_mask |= origin_bit
                    registrant_mask |= registrant_bit

            invalid_origin_masks.append(origin_mask)
            invalid_registrant_masks.append(registrant_mask)

        self._invalid_origin_masks[:] = invalid_origin_masks
        self._invalid_registrant_masks[:] = invalid_registrant_masks
