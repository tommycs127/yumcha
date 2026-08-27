"""Data models and function type aliases for conversion pipelines.

Defines reusable callable signatures and type aliases for resolving
representations and executing solver routines during conversions.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..models.representation import PhonologyRepresentation, SchemeRepresentation
    from ..models.solution import Solution

type SchemeRepresentationClsFn = Callable[
    [Scheme[SchemeRepresentation]], type[SchemeRepresentation]
]
"""Callable that resolves a scheme instance into its corresponding scheme representation class."""

type PhonologyRepresentationClsFn[P: PhonologyRepresentation] = Callable[
    [Scheme[SchemeRepresentation]], type[P]
]
"""Callable that resolves a scheme instance into its target phonological representation class."""

type SolveFn = Callable[[str, Scheme[SchemeRepresentation]], (Solution | None)]
"""Callable that executes conversion logic on a source text string and returns a `Solution` or `None`."""
