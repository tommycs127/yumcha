"""Helper functions for pattern tuple merging and validation in solving."""

from __future__ import annotations

from collections import defaultdict

from ..indexer import Indexer
from ..models.solution import Solution
from ..primitives.directives import SchemeDirective
from ..primitives.pattern_tuple import PatternTuple
from ..utils.bit import iterate_bits
from .models import SolveContext


def build_solution(
    context: SolveContext,
    candidate_mask: int,
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

    source_indexer = context.source_indexer
    source_pattern_tuples = source_indexer.pattern_tuples
    source_index_ranks = source_indexer.index_ranks
    source_directions = source_indexer.directions

    target_indexer = context.target_indexer
    target_pattern_tuples = target_indexer.pattern_tuples

    selected_indexes: list[int] = []
    directions: list[SchemeDirective] = []

    append_selected_index = selected_indexes.append
    append_direction = directions.append

    known_source = PatternTuple.wildcards(len(context.source_fields))
    known_target = PatternTuple.wildcards(len(context.target_fields))
    selected_mask = 0

    candidate_indexes: list[int] = list(iterate_bits(candidate_mask))
    candidate_indexes.sort(key=lambda idx: source_index_ranks[idx])

    for candidate_index in candidate_indexes:
        source_pattern_tuple = source_pattern_tuples[candidate_index]
        merged = union_if_compatible(known_source, source_pattern_tuple)
        if (merged is None) or (merged is known_source):
            continue
        known_source = merged

        target_pattern_tuple = target_pattern_tuples[candidate_index]
        merged = union_if_compatible(known_target, target_pattern_tuple)
        if (merged is None) or (merged is known_target):
            continue
        known_target = merged

        selected_mask |= 1 << candidate_index
        append_selected_index(candidate_index)

        source_direction = source_directions[candidate_index]
        append_direction(source_direction)

    if not (known_source.is_complete() and known_target.is_complete()):
        return None

    if not _is_valid(known_source, source_indexer, selected_mask):
        return None

    if not _is_valid(known_target, target_indexer, selected_mask):
        return None

    return Solution(
        source_indexer,
        target_indexer,
        known_source,
        known_target,
        tuple(selected_indexes),
        selected_mask,
        tuple(directions),
    )


def _is_valid(
    pattern_tuple: PatternTuple,
    indexer: Indexer,
    selected_mask: int,
) -> bool:
    """Validates that a pattern tuple does not contradict existing indexer constraints.

    Args:
        pattern_tuple: The pattern tuple to check.
        indexer: The indexer used to compute the pattern tuple.
            It contains the indexes of invalid pattern tuples.
        selected_mask: The bit mask containing the selected indexes
            to form the patterh tuple.

    Returns:
        `False` if `selected_mask` matches any index of an invalid pattern tuple;
            otherwise `True`.
    """
    invalid_mask_indexes: set[int] = set()
    invalid_pattern_masks_indexes_by_fields = (
        indexer.invalid_pattern_masks_indexes_by_fields
    )
    invalid_pattern_masks = indexer.invalid_pattern_masks

    for idx, pattern in enumerate(pattern_tuple):
        invalid_mask_indexes |= invalid_pattern_masks_indexes_by_fields[idx].get(
            pattern, frozenset()
        )

    invalid_masks: defaultdict[int, list[int]] = defaultdict(list)
    for mask_index in invalid_mask_indexes:
        mask = invalid_pattern_masks[mask_index]
        invalid_masks[mask].append(mask_index)

    for mask in invalid_masks:
        if (selected_mask & mask) == selected_mask:
            return False

    return True


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
    pattern_tuple_mask = pattern_tuple.mask
    collision_mask = known_pattern_tuple.mask & pattern_tuple_mask

    if collision_mask:
        if pattern_tuple_mask.bit_count() == 1:
            return known_pattern_tuple

        for idx in iterate_bits(collision_mask):
            if pattern_tuple[idx] != known_pattern_tuple[idx]:
                return None

    return known_pattern_tuple.union(pattern_tuple)
