"""Linear solver implementation for deterministic phonetic mapping.

Provides high-performance conversion for schemes with linear field dependencies.
Uses regex capture groups to decompose strings into fields, narrows down valid
registrants via bitwise mask intersection, and accumulates compatible pattern tuples.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, override

from ..models.representation import PhonologyRepresentation
from ..models.solution import Solution
from .base import BaseSolver
from .helpers import build_solution
from .models import SolveContext, SolveDirective

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..models.representation import SchemeRepresentation


class LinearSolver[PhonologyRepresentationT: PhonologyRepresentation](
    BaseSolver[PhonologyRepresentationT]
):
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
        registrant_mask = (1 << len(source_pattern_tuples.registrants)) - 1
        pattern_masks_by_fields = source_pattern_tuples.pattern_masks_by_fields

        for field_idx, pattern in enumerate(match.groups()):
            pattern_mask = pattern_masks_by_fields[field_idx][pattern]
            registrant_mask &= pattern_mask
            if registrant_mask == 0:
                return None

        return build_solution(context, registrant_mask)
