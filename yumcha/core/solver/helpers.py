"""Helper functions for pattern tuple merging and validation in CSP solving."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...core.utils.bit import iterate_bits

if TYPE_CHECKING:
    from ..primitives.pattern_tuple import PatternTuple


def merge_if_compatible(
    known_pattern_tuple: PatternTuple,
    pattern_tuple: PatternTuple,
) -> PatternTuple | None:
    """Merges two pattern tuples if their feature values do not conflict.

    Args:
        known_pattern_tuple: Accumulated pattern tuple representing current known state.
        pattern_tuple: New pattern tuple to merge in.

    Returns:
        The merged `PatternTuple` if compatible, or `None` if feature collisions conflict.
    """
    collision_mask = known_pattern_tuple.mask & pattern_tuple.mask

    if collision_mask:
        if pattern_tuple.mask.bit_count() == 1:
            return known_pattern_tuple

        for idx in iterate_bits(collision_mask):
            if pattern_tuple[idx] != known_pattern_tuple[idx]:
                return None

    return known_pattern_tuple.merge(pattern_tuple)
