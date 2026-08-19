"""Conversion pipeline validation component.

Provides rules and methods for verifying phonotactic constraint compliance and
roundtrip conversion fidelity across representations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ..exceptions import CollisionError, PhonologicalError, RoundtripError

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..language import Language
    from ..models.representation import (
        PhonologyRepresentation,
        Representation,
        SchemeRepresentation,
    )
    from ..models.solution import Solution


class ConversionValidator[PhonologyRepresentationT: PhonologyRepresentation]:
    """Handles phonotactic rule checks and roundtrip integrity verification."""

    def __init__(self, language: Language[PhonologyRepresentationT]) -> None:
        """Initializes the validator with the target language configuration.

        Args:
            language: Language facade instance.
        """
        self._language: Language[PhonologyRepresentationT] = language

    def validate(
        self,
        source: str,
        scheme: Scheme[SchemeRepresentation],
        solution: Solution,
        representation: Representation,
        inverse_solve_fn: Callable[
            [str, Scheme[SchemeRepresentation]],
            (Solution | None),
        ],
        inverse_cls_fn: Callable[
            [Scheme[SchemeRepresentation]],
            type[PhonologyRepresentationT | SchemeRepresentation],
        ],
        strict: bool = True,
    ) -> bool:
        """Runs phonotactic and roundtrip validations.

        Args:
            source: Original source text.
            scheme: Scheme instance being processed.
            solution: Primary conversion solution.
            representation: Converted target representation.
            inverse_solve_fn: Function to convert target string back to source domain.
            inverse_cls_fn: Function resolving source domain representation type.
            strict: If `True`, raises validation exceptions; if `False`, returns `False`.

        Returns:
            `True` if all validation checks pass; `False` if a check fails and `strict=False`.

        Raises:
            PhonologicalError: If phonotactic checks fail and `strict=True`.
            RoundtripError: If `source` fails to convert back to its original form
                inside the solver and `strict=True`.
            CollisionError: If a component collision occurs during round-trip validation
                and `strict=True`.
        """
        if self._has_phonotactic_violation(scheme, solution):
            if not strict:
                return False
            raise PhonologicalError(f"text {source!r} violates phonotactic rules")

        roundtrip_source = str(representation)
        roundtrip_solution = inverse_solve_fn(roundtrip_source, scheme)

        if roundtrip_solution is None:
            if not strict:
                return False
            raise RoundtripError(
                f"text {source!r} fails to roundtrip with scheme {scheme.id!r}"
            )

        roundtrip_representation = inverse_cls_fn(scheme)(
            *roundtrip_solution.target_pattern_tuple
        )

        if str(roundtrip_representation) != source:
            if not strict:
                return False
            expected_pattern_tuple = solution.source_pattern_tuple
            roundtrip_pattern_tuple = roundtrip_solution.target_pattern_tuple
            common_pattern_tuple = expected_pattern_tuple & roundtrip_pattern_tuple
            collided_source_pattern_tuple = (
                expected_pattern_tuple - common_pattern_tuple
            )
            collided_target_pattern_tuple = (
                roundtrip_pattern_tuple - common_pattern_tuple
            )
            source_debug_str = collided_source_pattern_tuple.to_debug_msg()
            target_debug_str = collided_target_pattern_tuple.to_debug_msg()
            raise CollisionError(
                f"colliding pattern tuples {source_debug_str} and {target_debug_str} "
                + f"for scheme {scheme.id!r}\n"
                + "To resolve this, inspect the scheme design for potential collisions and "
                + "explicitly mark them as invalid."
            )

        return True

    def _has_phonotactic_violation(
        self,
        scheme: Scheme[SchemeRepresentation],
        solution: Solution,
    ) -> bool:
        """Checks if a solution's origin mask violates forbidden phonotactic rules.

        Args:
            scheme: Target scheme definition holding invalid mask sets.
            solution: Solution containing origin indexes.

        Returns:
            `True` if any bitwise mask overlap indicates an illegal feature pattern, `False` otherwise.
        """
        invalid_origin_masks = scheme.intermediate_pattern_tuples.invalid_origin_masks
        origin_mask = sum(1 << origin_index for origin_index in solution.origin_indexes)
        return any(
            (origin_mask & invalid_mask) == origin_mask
            for invalid_mask in invalid_origin_masks
        )
