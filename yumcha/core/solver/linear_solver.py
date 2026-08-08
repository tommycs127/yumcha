"""Linear solver implementation for deterministic phonetic mapping.

Provides high-performance conversion for schemes with linear field dependencies.
Uses regex capture groups to decompose strings into fields, narrows down valid
registrants via bitwise mask intersection, and accumulates compatible pattern tuples.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from ..models.solution import Solution
from ..primitives.directives import SchemeDirective
from ..primitives.pattern_tuple import PatternTuple
from ..utils.bit import iterate_bits
from .base import BaseSolver
from .helpers import merge_if_compatible
from .models import SolveContext, SolveDirective

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..models.representation import SchemeRepresentation


class LinearSolver(BaseSolver):
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
    ) -> Solution | None:
        """Sets up the solve context and executes search pipeline for a given direction.

        Args:
            text: Raw input text string.
            scheme: Scheme facade instance.
            directive: Direction of conversion (`INTERMEDIATE_TO_SCHEME` or vice-versa).

        Returns:
            Resolved `Solution` or `None`.
        """
        phonology = self.language.phonology

        if directive is SolveDirective.INTERMEDIATE_TO_SCHEME:
            canonicalizer = phonology.canonicalizer
            source_pattern_tuples = scheme.intermediate_pattern_tuples
            target_pattern_tuples = scheme.pattern_tuples
            source_fields = phonology.fields
            target_fields = tuple(scheme.fields)
        else:
            canonicalizer = scheme.canonicalizer
            source_pattern_tuples = scheme.pattern_tuples
            target_pattern_tuples = scheme.intermediate_pattern_tuples
            source_fields = tuple(scheme.fields)
            target_fields = phonology.fields

        text_norm = canonicalizer.canonicalize(text)

        context = SolveContext(
            text_norm,
            scheme,
            directive,
            source_pattern_tuples,
            target_pattern_tuples,
            source_fields,
            target_fields,
            scheme.fields,
        )

        return self._solve(context)

    def _solve(self, context: SolveContext) -> Solution | None:
        """Performs search execution over generated candidates and validates pattern tuples.

        Args:
            context: Pre-configured solving context containing scheme and directional metadata.

        Returns:
            A valid `Solution` if all field conditions and pattern tuple masks pass, otherwise `None`.
        """
        re_pattern = (
            self.language.phonology.re_pattern
            if context.directive is SolveDirective.INTERMEDIATE_TO_SCHEME
            else context.scheme.re_pattern
        )
        match = re.fullmatch(re_pattern, context.text_norm)
        if match is None:
            return None

        source_pattern_tuples = context.source_pattern_tuples
        target_pattern_tuples = context.target_pattern_tuples
        source_registrants = source_pattern_tuples._registrants

        registrant_mask = (1 << len(source_registrants)) - 1
        pattern_masks_by_fields = context.source_pattern_tuples.pattern_masks_by_fields

        for field_idx, pattern in enumerate(match.groups()):
            pattern_mask = pattern_masks_by_fields[field_idx][pattern]
            registrant_mask &= pattern_mask
            if registrant_mask == 0:
                return None

        known_source = PatternTuple.wildcards(len(context.source_fields))
        known_target = PatternTuple.wildcards(len(context.target_fields))
        origin_indexes: list[int] = []
        registrant_indexes: list[int] = []
        directions: list[SchemeDirective] = []

        for registrant_index in iterate_bits(registrant_mask):
            (
                origin_index,
                source_pattern_tuple,
                direction,
                _,
            ) = source_registrants[registrant_index]

            merged = merge_if_compatible(known_source, source_pattern_tuple)
            if (merged is None) or (merged is known_source):
                continue
            known_source = merged

            target_pattern_tuple = (
                target_pattern_tuples.registrant_by_origin_index(origin_index)
            )[1]

            merged = merge_if_compatible(known_target, target_pattern_tuple)
            if (merged is None) or (merged is known_target):
                continue
            known_target = merged

            origin_indexes.append(origin_index)
            registrant_indexes.append(registrant_index)
            directions.append(direction)

        return Solution(
            known_source,
            known_target,
            tuple(origin_indexes),
            tuple(registrant_indexes),
            registrant_mask,
            tuple(directions),
        )
