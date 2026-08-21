"""Helper functions for pattern tuple merging and validation in solving."""

from __future__ import annotations

from ..models.solution import Solution
from ..primitives.directives import SchemeDirective
from ..primitives.pattern_tuple import PatternTuple
from ..utils.bit import iterate_bits
from .models import SolveContext


def build_solution(
    context: SolveContext,
    registrant_mask: int,
) -> Solution | None:
    """Validates unified pattern tuples and global origin constraints
    to construct a Solution.

    Args:
        context: Active solve context containing source/target pattern tuples.
        registrant_mask: Bitmask representing candidate active registrants.

    Returns:
        A fully validated `Solution` instance, or `None` if unification fails
        or matches invalid origin masks.
    """

    source_pattern_tuples = context.source_pattern_tuples
    target_pattern_tuples = context.target_pattern_tuples
    source_registrants = source_pattern_tuples.registrants

    origin_indexes: list[int] = []
    registrant_indexes: list[int] = []
    directions: list[SchemeDirective] = []

    known_source = PatternTuple.wildcards(len(context.source_fields))
    known_target = PatternTuple.wildcards(len(context.target_fields))
    origin_mask = 0

    for registrant_index in iterate_bits(registrant_mask):
        (
            origin_index,
            source_pattern_tuple,
            direction,
            _,
        ) = source_registrants[registrant_index]

        merged = union_if_compatible(known_source, source_pattern_tuple)
        if (merged is None) or (merged is known_source):
            continue
        known_source = merged

        target_pattern_tuple = target_pattern_tuples.registrant_by_origin_index(
            origin_index
        )[1]

        merged = union_if_compatible(known_target, target_pattern_tuple)
        if (merged is None) or (merged is known_target):
            continue
        known_target = merged

        origin_mask |= 1 << origin_index

        registrant_indexes.append(registrant_index)
        origin_indexes.append(origin_index)
        directions.append(direction)

    if not (known_source.is_complete() and known_target.is_complete()):
        return None

    scheme = context.scheme
    invalid_intermediate_masks = scheme.intermediate_pattern_tuples.invalid_origin_masks
    invalid_origin_masks = scheme.pattern_tuples.invalid_origin_masks

    if any(
        (origin_mask & invalid_mask) == origin_mask
        for invalid_mask in invalid_intermediate_masks
    ):
        return None

    if any(
        (origin_mask & invalid_mask) == origin_mask
        for invalid_mask in invalid_origin_masks
    ):
        return None

    return Solution(
        known_source,
        known_target,
        tuple(origin_indexes),
        tuple(registrant_indexes),
        registrant_mask,
        tuple(directions),
    )


def union_if_compatible(
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

    return known_pattern_tuple.union(pattern_tuple)
