"""Constraint Satisfaction Problem (CSP) solver implementation.

Solves phonological and orthographic conversions by searching candidate pattern combinations,
enforcing feature compatibility, and eliminating invalid registrant masks.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from types import EllipsisType
from typing import TYPE_CHECKING, override

from ..models.solution import Solution
from ..utils.bit import iterate_bits
from .base import BaseSolver
from .helpers import build_solution
from .models import (
    Candidate,
    SearchState,
    SearchStateMRV,
    SolveContext,
    SolveDirective,
)

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..models.representation import PhonologyRepresentation, SchemeRepresentation

ELLIPSIS = ...
EMPTY_STR = ""
INF = float("inf")


class CSPSolver[PhonologyRepresentationT: PhonologyRepresentation](
    BaseSolver[PhonologyRepresentationT]
):
    """CSP-based solver for resolving text patterns to representation solutions."""

    @override
    def solve_intermediate(
        self,
        text: str,
        scheme: Scheme[SchemeRepresentation],
    ) -> Solution | None:
        """Solves an intermediate phonological representation into a scheme solution.

        Args:
            text: Phonological representation text to convert.
            scheme: Target orthographic scheme.

        Returns:
            A resolved `Solution` instance, or `None` if no compatible solution exists.
        """
        return self._solve_pipeline(text, scheme, SolveDirective.INTERMEDIATE_TO_SCHEME)

    @override
    def solve_scheme(
        self,
        text: str,
        scheme: Scheme[SchemeRepresentation],
    ) -> Solution | None:
        """Solves a scheme orthographic string into an intermediate phonological solution.

        Args:
            text: Scheme orthographic text to convert.
            scheme: Source orthographic scheme.

        Returns:
            A resolved `Solution` instance, or `None` if no compatible solution exists.
        """
        return self._solve_pipeline(text, scheme, SolveDirective.SCHEME_TO_INTERMEDIATE)

    def _solve_pipeline(
        self,
        text: str,
        scheme: Scheme[SchemeRepresentation],
        directive: SolveDirective,
        use_solver_with_mrv: bool = False,
    ) -> Solution | None:
        """Sets up the solve context and executes search pipeline for a given direction.

        Args:
            text: Raw input text string.
            scheme: Scheme facade instance.
            directive: Direction of conversion (`INTERMEDIATE_TO_SCHEME` or vice-versa).
            use_solver_with_mrv: Whether to use Minimum Remaining Values search heuristic.

        Returns:
            Resolved `Solution` or `None`.
        """
        phonology = self.language.phonology

        if directive is SolveDirective.INTERMEDIATE_TO_SCHEME:
            canonicalizer = phonology.canonicalizer
            source_indexer = scheme.intermediate_indexer
            target_indexer = scheme.indexer
            source_fields = phonology.fields
            target_fields = tuple(scheme.fields)
        else:
            canonicalizer = scheme.canonicalizer
            source_indexer = scheme.indexer
            target_indexer = scheme.intermediate_indexer
            source_fields = tuple(scheme.fields)
            target_fields = phonology.fields

        text_norm = canonicalizer.canonicalize(text)

        context = SolveContext(
            text_norm,
            scheme,
            directive,
            source_indexer,
            target_indexer,
            source_fields,
            target_fields,
            scheme.fields,
        )

        return self._solve(context, use_solver_with_mrv)

    def _solve(
        self,
        context: SolveContext,
        use_solver_with_mrv: bool = False,
    ) -> Solution | None:
        """Performs search execution over generated candidates and validates pattern tuples.

        Args:
            context: Pre-configured solving context containing scheme and directional metadata.
            use_solver_with_mrv: Whether to use Minimum Remaining Values search heuristic.

        Returns:
            A valid `Solution` if all field conditions and pattern tuple masks pass, otherwise `None`.
        """
        candidates = self._find_candidates(context)
        if candidates is None:
            return None

        source_pattern_tuples = context.source_indexer.pattern_tuples

        full_registrant_mask = (1 << len(source_pattern_tuples)) - 1

        if use_solver_with_mrv:
            full_fields_mask = (1 << len(context.source_fields)) - 1
            init_state = SearchStateMRV(full_fields_mask, full_registrant_mask, ())
            solution_iterator = self._find_solution_mrv(context, candidates, init_state)
        else:
            init_state = SearchState(0, full_registrant_mask, ())
            solution_iterator = self._find_solution(context, candidates, init_state)

        for state in solution_iterator:
            if state.selected_text != context.text_norm:
                continue

            solution = build_solution(context, state.registrant_mask)
            if solution is not None:
                return solution

        return None

    def _find_candidates(self, context: SolveContext) -> list[list[Candidate]] | None:
        """Finds matching candidate patterns for each field slot in source text.

        Args:
            context: Solving context holding text and pattern tuples.

        Returns:
            List of candidate lists per slot index, or `None` if any slot has zero candidates.
        """
        text_norm = context.text_norm
        source_fields = context.source_fields
        source_fields_length = len(source_fields)

        candidates: list[list[Candidate]] = [[] for _ in range(source_fields_length)]
        pattern_masks_by_fields = context.source_indexer.pattern_masks_by_fields

        last_slot_idx = source_fields_length - 1

        for idx, pattern_masks in enumerate(pattern_masks_by_fields):
            is_first = idx == 0
            is_last = idx == last_slot_idx

            field_candidates = candidates[idx]

            for pattern, pattern_mask in pattern_masks.items():
                if isinstance(pattern, EllipsisType):
                    continue

                not_startswith_pattern = is_first and not text_norm.startswith(pattern)
                not_endswith_pattern = is_last and not text_norm.endswith(pattern)
                if not_startswith_pattern or not_endswith_pattern:
                    continue

                if pattern is EMPTY_STR:
                    candidate = Candidate(pattern, pattern_mask, None)
                    field_candidates.append(candidate)
                    continue

                for match in re.finditer(re.escape(pattern), text_norm):
                    candidate = Candidate(pattern, pattern_mask, match.span())
                    field_candidates.append(candidate)

            if len(field_candidates) == 0:
                return None

            field_candidates.sort(key=lambda item: len(item.pattern), reverse=True)

        return candidates

    def _find_solution(
        self,
        context: SolveContext,
        candidates: list[list[Candidate]],
        state: SearchState,
    ) -> Iterator[SearchState]:
        """Recursively yields candidate combinations using linear depth-first search.

        Args:
            context: Solving context.
            candidates: Candidate choices per slot.
            state: Active search state.

        Yields:
            `SearchState` instances representing complete assignments.
        """
        field_index = state.field_index
        if field_index >= len(context.source_fields):
            yield state
            return

        for candidate in candidates[field_index]:
            new_candidate_mask = state.registrant_mask & candidate.registrant_mask
            if new_candidate_mask == 0:
                continue

            new_state = SearchState(
                state.field_index + 1,
                new_candidate_mask,
                (*state.selected, candidate),
            )
            yield from self._find_solution(context, candidates, new_state)

    def _find_solution_mrv(
        self,
        context: SolveContext,
        candidates: list[list[Candidate]],
        state: SearchStateMRV,
    ) -> Iterator[SearchStateMRV]:
        """Recursively yields candidate combinations using Minimum Remaining Values heuristic.

        This strategy is for internal debugging only and is not intended for public exposure.

        Args:
            context: Solving context.
            candidates: Candidate choices per slot.
            state: Active MRV search state.

        Yields:
            `SearchStateMRV` instances representing complete assignments.
        """
        remaining_fields_mask = state.remaining_fields_mask
        if remaining_fields_mask == 0:
            yield state
            return

        best_count = INF
        best_field_index = None

        for field_index in iterate_bits(remaining_fields_mask):
            count = sum(
                1
                for candidate in candidates[field_index]
                if state.registrant_mask & candidate.registrant_mask
            )

            if count == 0:
                return

            if count < best_count:
                best_count = count
                best_field_index = field_index

        if best_field_index is None:  # fail-safe for type checkers
            return

        for candidate in candidates[best_field_index]:
            new_registrant_mask = state.registrant_mask & candidate.registrant_mask
            if new_registrant_mask == 0:
                continue

            new_state = SearchStateMRV(
                state.remaining_fields_mask & ~(1 << best_field_index),
                new_registrant_mask,
                (*state.selected, (best_field_index, candidate)),
            )
            yield from self._find_solution_mrv(context, candidates, new_state)
