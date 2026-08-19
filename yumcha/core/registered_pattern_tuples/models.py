"""Data models and type aliases for registered pattern tuples.

Provides data structures representing individual registered pattern tuples along
with type aliases for pattern bitmasks used during constraint compilation.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from ..primitives.directives import SchemeDirective
    from ..primitives.pattern import Pattern
    from ..primitives.pattern_tuple import PatternTuple

type PatternMasks = dict[Pattern, int]
"""Mapping from a pattern to a bitmask representing pattern tuple indices."""

type PatternMasksView = MappingProxyType[Pattern, int]
"""Read-only view of a `PatternMasks` mapping."""


class RegisteredPatternTuple(NamedTuple):
    """Container for a pattern tuple and its registration metadata.

    Attributes:
        origin_index (int): Original zero-based index of the pattern tuple before sorting.
        pattern_tuple (PatternTuple): The underlying pattern tuple object.
        direction (SchemeDirective): Directive specifying the operational direction/scheme.
        pattern_tuple_weight (int): The calculated priority/weight used for sorting pattern tuples.
    """

    origin_index: int
    pattern_tuple: PatternTuple
    direction: SchemeDirective
    pattern_tuple_weight: int
