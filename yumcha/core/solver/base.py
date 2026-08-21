"""Abstract base solver definition.

Provides the foundational interface and shared language context for solvers
resolving phonological representations and orthographic schemes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..language import Language
    from ..models.representation import PhonologyRepresentation, SchemeRepresentation
    from ..models.solution import Solution


class BaseSolver[PhonologyRepresentationT: PhonologyRepresentation](ABC):
    """Abstract base class defining the uniform interface for all text solvers."""

    def __init__(self, language: Language[PhonologyRepresentationT]) -> None:
        """Initializes the solver with a target language grammar model.

        Args:
            language: Language facade instance containing phonology and scheme models.
        """
        self.language: Language[PhonologyRepresentationT] = language

    @abstractmethod
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

    @abstractmethod
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
