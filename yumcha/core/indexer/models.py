"""Data models and type aliases for indexer.

Provides data structures representing individual registered pattern tuples along
with type aliases for pattern bitmasks used during constraint compilation.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..primitives.pattern import Pattern

type PatternMasks = dict[Pattern, int]
"""Mapping from a pattern to a bitmask representing pattern tuple indices."""

type PatternMasksView = MappingProxyType[Pattern, int]
"""Read-only view of a `PatternMasks` mapping."""

type PatternIndexes = dict[Pattern, set[int]]
"""Mapping from a pattern token to a mutable set of invalid pattern tuple indices."""

type PatternIndexesView = MappingProxyType[Pattern, frozenset[int]]
"""Read-only view mapping a pattern token to an immutable set of invalid pattern tuple indices."""
