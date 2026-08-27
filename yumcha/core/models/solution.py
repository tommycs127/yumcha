"""Data models for solved pattern tuple conversions.

Provides dataclass structures for representing resolved conversion mappings between
source and target phonological pattern tuples.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..indexer import Indexer
    from ..primitives.directives import SchemeDirective
    from ..primitives.pattern_tuple import PatternTuple


@dataclass(frozen=True)
class Solution:
    """Represents a resolved conversion mapping between phonological pattern tuples.

    Attributes:
        source_indexer: Indexer in the source domain used.
        target_indexer: Indexer in the target domain used.
        source_pattern_tuple: Resolved pattern tuple in the source domain.
        target_pattern_tuple: Resolved pattern tuple in the target domain.
        selected_indexes: Tuple of matching pattern rule indexes.
        selected_mask: Combined integer bitmask representing registered pattern tuple states.
        directions: Directives specifying directional mapping pattern tuples for rules used.
    """

    source_indexer: Indexer
    target_indexer: Indexer
    source_pattern_tuple: PatternTuple
    target_pattern_tuple: PatternTuple
    selected_indexes: tuple[int, ...]
    selected_mask: int
    directions: tuple[SchemeDirective, ...]
