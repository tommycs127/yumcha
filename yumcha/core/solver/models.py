"""Data models and search state structures for CSP solving.

Defines directives, search contexts, candidates, and state representations
for standard and Minimum Remaining Values (MRV) search algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from operator import itemgetter
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..indexer import Indexer
    from ..models.representation import SchemeRepresentation


class SolveDirective(Enum):
    """Specifies the direction of conversion during pattern tuple solving."""

    INTERMEDIATE_TO_SCHEME = 1
    SCHEME_TO_INTERMEDIATE = 2


@dataclass(frozen=True)
class SolveContext:
    """Encapsulates static parameters and target scheme data for a solver execution.

    Attributes:
        text_norm: Canonicalized source text to solve.
        scheme: The active target or source `Scheme` facade.
        directive: The direction of conversion (`INTERMEDIATE_TO_SCHEME` or vice-versa).
        source_indexer: Indexed pattern tuples for the source domain.
        target_indexer: Indexed pattern tuples for the target domain.
        source_fields: Field names for the source representation.
        target_fields: Field names for the target representation.
        scheme_to_intermediate_map: Mapping of scheme fields to intermediate indices.
    """

    text_norm: str
    scheme: Scheme[SchemeRepresentation]
    directive: SolveDirective
    source_indexer: Indexer
    target_indexer: Indexer
    source_fields: tuple[str, ...]
    target_fields: tuple[str, ...]
    scheme_to_intermediate_map: MappingProxyType[str, frozenset[int]]


@dataclass(frozen=True)
class Candidate:
    """Represents a candidate pattern match within a field slot.

    Attributes:
        pattern: The matched string pattern.
        registrant_mask: Bitmask of valid registrants associated with this pattern.
        span: Character offset range `(start, end)` in the source text, or `None` if empty.
    """

    pattern: str
    registrant_mask: int
    span: tuple[int, int] | None

    @cached_property
    def str_mask(self) -> int:
        """Computes a bitmask representing the character span coverage in source text.

        Returns:
            An integer bitmask with bits set for each matched character position.
        """
        if self.span is None:
            return 0
        start, end = self.span
        return ((1 << (end - start)) - 1) << start


@dataclass(frozen=True)
class SearchState:
    """Tracks linear depth-first search state across field indices.

    Attributes:
        field_index: Current field index being processed.
        registrant_mask: Combined bitmask of surviving compatible registrants.
        selected: Sequence of chosen `Candidate` matches.
    """

    field_index: int
    registrant_mask: int
    selected: tuple[Candidate, ...]

    @property
    def selected_text(self) -> str:
        """Concatenates candidate patterns into the assembled output text.

        Returns:
            The combined source or target string for currently selected candidates.
        """
        return "".join(candidate.pattern for candidate in self.selected)


@dataclass(frozen=True)
class SearchStateMRV:
    """Tracks state for Minimum Remaining Values (MRV) heuristic depth-first search.

    Attributes:
        remaining_fields_mask: Bitmask indicating remaining unassigned fields.
        registrant_mask: Combined bitmask of surviving compatible registrants.
        selected: Tuples of `(field_index, Candidate)` for made assignments.
    """

    remaining_fields_mask: int
    registrant_mask: int
    selected: tuple[tuple[int, Candidate], ...]

    @property
    def selected_text(self) -> str:
        """Concatenates selected candidate patterns ordered by original field index.

        Returns:
            The assembled string reconstituted in field-index sequence order.
        """
        return "".join(
            candidate.pattern
            for _, candidate in sorted(self.selected, key=itemgetter(0))
        )
