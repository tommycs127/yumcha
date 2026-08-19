"""Conversion pipeline orchestrator.

Provides high-level methods to convert between orthographic schemes and underlying
phonological representations with automatic validation and strict error boundaries.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Literal, overload

from ..exceptions import NoMatchError
from .validation import ConversionValidator

if TYPE_CHECKING:
    from ..facades.scheme import Scheme
    from ..language import Language
    from ..models.representation import PhonologyRepresentation, SchemeRepresentation
    from ..models.solution import Solution


class ConversionPipeline[PhonologyRepresentationT: PhonologyRepresentation]:
    """Orchestrates conversion, phonotactic validation, and roundtrip checking."""

    type SchemeRepresentationClsFn = Callable[
        [Scheme[SchemeRepresentation]], type[SchemeRepresentation]
    ]
    type PhonologyRepresentationClsFn[P: PhonologyRepresentation] = Callable[
        [Scheme[SchemeRepresentation]], type[PhonologyRepresentationT]
    ]
    type SolveFn = Callable[[str, Scheme[SchemeRepresentation]], (Solution | None)]

    def __init__(self, language: Language[PhonologyRepresentationT]) -> None:
        """Initializes the conversion pipeline for a given language model.

        Args:
            language: Language facade instance containing solvers, phonology, and schemes.
        """
        self._language: Language[PhonologyRepresentationT] = language
        self._validator: ConversionValidator[PhonologyRepresentationT] = (
            ConversionValidator(language)
        )

    def convert_to_intermediate(
        self,
        source: str,
        scheme_id: str,
        validate: bool = True,
        strict: bool = True,
        solver_id: str | None = None,
    ) -> PhonologyRepresentationT | None:
        """Converts an orthographic scheme string into its intermediate phonological representation.

        Args:
            source: Source scheme string to convert.
            scheme_id: Identifier of the source scheme.
            validate: Whether to run phonotactic and roundtrip integrity checks.
            strict: If `True`, raises errors on failure; if `False`, returns `None`.
            solver_id: Identifier of the solver to resolve source text into a solution.
                If `None`, picks the default solver from `self._language._solver_to_use`.

        Returns:
            An instance of `PhonologyRepresentationT`, or `None` if conversion fails and `strict=False`.

        Raises:
            KeyError: If `solver_id` is not in `self._language._solvers`.
        """
        language = self._language
        if solver_id is None:
            solver_id = language.solver_to_use[scheme_id]
        solver = language.solvers[solver_id]
        return self._execute(
            source,
            scheme_id,
            solver.solve_scheme,
            lambda _: language.phonology.cls,
            solver.solve_intermediate,
            lambda scheme: scheme.cls,
            validate,
            strict,
        )

    def convert_to_scheme(
        self,
        source: str,
        scheme_id: str,
        validate: bool = True,
        strict: bool = True,
        solver_id: str | None = None,
    ) -> SchemeRepresentation | None:
        """Converts an intermediate phonological representation string into a target scheme representation.

        Args:
            source: Source phonological string to convert.
            scheme_id: Identifier of the target scheme.
            validate: Whether to run phonotactic and roundtrip integrity checks.
            strict: If `True`, raises errors on failure; if `False`, returns `None`.
            solver_id: Identifier of the solver to resolve source text into a solution.
                If `None`, picks the default solver in `self._language`.

        Returns:
            An instance of `SchemeRepresentation`, or `None` if conversion fails and `strict=False`.

        Raises:
            KeyError: If `solver_id` is not in `self._language._solvers`.
        """
        language = self._language
        if solver_id is None:
            solver_id = language.solver_to_use[scheme_id]
        solver = language.solvers[solver_id]
        return self._execute(
            source,
            scheme_id,
            solver.solve_intermediate,
            lambda scheme: scheme.cls,
            solver.solve_scheme,
            lambda _: language.phonology.cls,
            validate,
            strict,
        )

    @overload
    def _execute(
        self,
        source: str,
        scheme_id: str,
        solve_fn: SolveFn,
        target_cls_fn: SchemeRepresentationClsFn,
        inverse_solve_fn: SolveFn,
        inverse_cls_fn: PhonologyRepresentationClsFn[PhonologyRepresentationT],
        validate: bool,
        strict: Literal[True] = ...,
    ) -> SchemeRepresentation: ...

    @overload
    def _execute(
        self,
        source: str,
        scheme_id: str,
        solve_fn: SolveFn,
        target_cls_fn: SchemeRepresentationClsFn,
        inverse_solve_fn: SolveFn,
        inverse_cls_fn: PhonologyRepresentationClsFn[PhonologyRepresentationT],
        validate: bool,
        strict: Literal[False] = ...,
    ) -> SchemeRepresentation | None: ...

    @overload
    def _execute(
        self,
        source: str,
        scheme_id: str,
        solve_fn: SolveFn,
        target_cls_fn: PhonologyRepresentationClsFn[PhonologyRepresentationT],
        inverse_solve_fn: SolveFn,
        inverse_cls_fn: SchemeRepresentationClsFn,
        validate: bool,
        strict: Literal[True] = ...,
    ) -> PhonologyRepresentationT: ...

    @overload
    def _execute(
        self,
        source: str,
        scheme_id: str,
        solve_fn: SolveFn,
        target_cls_fn: PhonologyRepresentationClsFn[PhonologyRepresentationT],
        inverse_solve_fn: SolveFn,
        inverse_cls_fn: SchemeRepresentationClsFn,
        validate: bool,
        strict: Literal[False] = ...,
    ) -> PhonologyRepresentationT | None: ...

    def _execute(
        self,
        source: str,
        scheme_id: str,
        solve_fn: SolveFn,
        target_cls_fn: SchemeRepresentationClsFn
        | PhonologyRepresentationClsFn[PhonologyRepresentationT],
        inverse_solve_fn: SolveFn,
        inverse_cls_fn: PhonologyRepresentationClsFn[PhonologyRepresentationT]
        | SchemeRepresentationClsFn,
        validate: bool,
        strict: bool = True,
    ) -> PhonologyRepresentationT | SchemeRepresentation | None:
        """Executes conversion pipeline between phonology and scheme representations.

        Handles solving input pattern tuples, instantiating target representation dataclasses,
        and running phonotactic and roundtrip consistency checks.

        Args:
            source: Raw string input to transform.
            scheme_id: Identifier of the registered target scheme.
            solve_fn: Function to resolve source text into a `Solution`.
            target_cls_fn: Resolver function returning the target representation class.
            inverse_solve_fn: Function used during roundtrip verification to solve back.
            inverse_cls_fn: Resolver function returning the source representation class.
            validate: Whether to validate phonotactics and roundtrip integrity.
            strict: If True, raises exceptions on errors; if False, returns None.

        Returns:
            An instance of target representation dataclass, or None if conversion fails
            and `strict=False`.

        Raises:
            NoMatchError: If `solve_fn` returns no solution and `strict=True`.
            PhonologicalError: If input violates phonotactic rules and `strict=True`.
            NotSupportedError: If roundtrip verification fails and `strict=True`.
        """
        scheme = self._language.schemes[scheme_id]
        solution = self._solve_or_raise(solve_fn, source, scheme, strict)
        if solution is None:
            return None

        representation = target_cls_fn(scheme)(*solution.target_pattern_tuple)

        if validate:
            is_valid = self._validator.validate(
                source,
                scheme,
                solution,
                representation,
                inverse_solve_fn,
                inverse_cls_fn,
                strict,
            )
            if not is_valid:
                return None

        return representation

    @overload
    def _solve_or_raise(
        self,
        solve_fn: SolveFn,
        source: str,
        scheme: Scheme[SchemeRepresentation],
        strict: Literal[True] = ...,
    ) -> Solution: ...

    @overload
    def _solve_or_raise(
        self,
        solve_fn: SolveFn,
        source: str,
        scheme: Scheme[SchemeRepresentation],
        strict: Literal[False] = ...,
    ) -> Solution | None: ...

    def _solve_or_raise(
        self,
        solve_fn: SolveFn,
        source: str,
        scheme: Scheme[SchemeRepresentation],
        strict: bool = True,
    ) -> Solution | None:
        """Executes a solver function and enforces strict error boundary rules.

        Args:
            solve_fn: Solver function mapping text and scheme to a `Solution`.
            source: Source text string to solve.
            scheme: Target `Scheme` instance.
            strict: If True, raises `NoMatchError` on solver failure; if False, returns None.

        Returns:
            A resolved `Solution` instance, or None if `strict=False` and solving fails.

        Raises:
            NoMatchError: If `solve_fn` returns None and `strict=True`.
        """
        solution = solve_fn(source, scheme)
        if solution is None:
            if not strict:
                return None
            raise NoMatchError(f"invalid text {source!r} for scheme {scheme.id!r}")
        return solution
