"""Data models for solved pattern_tuple conversions.

Provides dataclass structures for representing resolved conversion mappings between
source and target phonological pattern_tuples.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..primitives.directives import SchemeDirective
    from ..primitives.pattern import Pattern
    from ..primitives.pattern_tuple import PatternTuple


@dataclass(frozen=True)
class Solution:
    """Represents a resolved conversion mapping between phonological pattern_tuples.

    Attributes:
        source_pattern_tuple: Resolved pattern tuple in the source domain.
        target_pattern_tuple: Resolved pattern tuple in the target domain.
        origin_indexes: Tuple of matching pattern rule indexes from original spec.
        registrant_indexes: Tuple of registered pattern tuple indexes applied during solving.
        registrant_mask: Combined integer bitmask representing registered pattern tuple states.
        directions: Directives specifying directional mapping pattern tuples for rules used.
    """

    source_pattern_tuple: PatternTuple
    target_pattern_tuple: PatternTuple
    origin_indexes: tuple[int, ...]
    registrant_indexes: tuple[int, ...]
    registrant_mask: int
    directions: tuple[SchemeDirective, ...]
