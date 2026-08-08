"""Language facade coordinating phonological representations and orthographic schemes."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, overload

from .conversion_pipeline import ConversionPipeline
from .exceptions import ParseError, SchemeError
from .primitives.directives import PhonologyDirective
from .solver import CSPSolver, LinearSolver

if TYPE_CHECKING:
    from .facades.phonology import Phonology
    from .facades.scheme import Scheme
    from .models.representation import PhonologyRepresentation, SchemeRepresentation
    from .solver.base import BaseSolver


type SupportedSolvers = Literal["csp", "linear"]


class Language[PhonologyRepresentationT: PhonologyRepresentation]:
    """Coordinates phonological representations and orthographic/romanization schemes.

    Provides high-level APIs for converting phoneme representations to/from registered
    schemes, cross-converting between schemes, running validations, and generating
    combinatorial syllable tables.
    """

    def __init__(self, phonology: Phonology[PhonologyRepresentationT]) -> None:
        """Initializes a Language instance with a phonology spec.

        Args:
            phonology: `Phonology` instance containing character sets and phonotactic rules.
        """
        self._phonology = phonology

        self._schemes: dict[str, Scheme[SchemeRepresentation]] = {}
        self._schemes_view: MappingProxyType[str, Scheme[SchemeRepresentation]] = (
            MappingProxyType(self._schemes)
        )

        self._solvers: dict[str, BaseSolver] = {
            "csp": CSPSolver(self),
            "linear": LinearSolver(self),
        }
        self._solver_to_use: dict[str, SupportedSolvers] = {}
        self._pipeline = ConversionPipeline(self)

    @property
    def phonology(self) -> Phonology[PhonologyRepresentationT]:
        """Gets the underlying phonology specification."""
        return self._phonology

    @property
    def schemes(self) -> MappingProxyType[str, Scheme[SchemeRepresentation]]:
        """Gets a read-only view of registered scheme facades.

        Returns:
            MappingProxyType mapping scheme ID strings to Scheme instances.
        """
        return self._schemes_view

    def add_scheme(self, scheme: Scheme[SchemeRepresentation]) -> None:
        """Loads, validates, and registers a scheme mapping.

        Args:
            scheme: File path string, `Traversable` resource, or pre-built `Scheme` object.

        Raises:
            ValueError: If character sets in the scheme conflict with phonology requirements.
        """
        self.validate_scheme(scheme)
        scheme.intermediate_pattern_tuples.build_invalid_masks(
            self._phonology.invalid_pattern_tuples
        )
        self._schemes[scheme.id] = scheme
        if scheme.are_field_indexes_sequential:
            self._solver_to_use[scheme.id] = "linear"
        else:
            self._solver_to_use[scheme.id] = "csp"

    def validate_scheme(self, scheme: Scheme[SchemeRepresentation]) -> None:
        """Validates that a scheme covers all required phonology character sets.

        Args:
            scheme: `Scheme` instance to validate against the active phonology.

        Raises:
            ValueError: If phonemes required by phonology are missing in the scheme,
                or if redundant phonemes are present in the scheme.
        """
        phonology_directive_maps = self.phonology.phonology_directive_maps
        charsets_classified = self.phonology.charsets_classified
        scheme_ic_charsets = scheme.intermediate_pattern_tuples.charsets

        for idx, phonology_charset in enumerate(phonology_directive_maps):
            phonology_required = charsets_classified[idx][PhonologyDirective.REQUIRED]
            scheme_charset = scheme_ic_charsets[idx]

            if missing_charset := (phonology_required.difference(scheme_charset)):
                raise SchemeError(
                    f"missing phonemes for {self.phonology.fields[idx]}: "
                    f"add {sorted(missing_charset)}"
                )

            if redundant_charset := (scheme_charset.difference(set(phonology_charset))):
                raise SchemeError(
                    f"redundant phonemes for {self.phonology.fields[idx]}: "
                    f"remove {sorted(redundant_charset)}"
                )

    def remove_scheme(self, scheme_id: str) -> Scheme[SchemeRepresentation]:
        """Removes and returns a registered scheme by ID.

        Args:
            scheme_id: Identifier of the scheme to unregister.

        Returns:
            The removed `Scheme` instance.

        Raises:
            KeyError: If `scheme_id` is not registered.
        """
        self._solver_to_use.pop(scheme_id)
        return self._schemes.pop(scheme_id)

    def parse_to_intermediate(self, text: str) -> PhonologyRepresentationT:
        """Parses text into a phonological intermediate `Representation`.

        Args:
            text: Raw input string to parse.

        Returns:
            An instantiated intermediate `Representation` dataclass.

        Raises:
            ParseError: If input text fails to match the expected phonology pattern.
        """
        match = self._phonology.compiled_re_pattern.fullmatch(text)
        if match is None:
            raise ParseError(f"failed to parse text {text!r}")
        return self._phonology.cls(*match.groups())

    def parse_to_scheme(self, text: str, scheme_id: str) -> SchemeRepresentation:
        """Parses text into the target scheme's `Representation`.

        Args:
            text: Raw input string to parse.
            scheme_id: Identifier of the target registered scheme.

        Returns:
            An instantiated target scheme `Representation` dataclass.

        Raises:
            KeyError: If `scheme_id` is not registered.
            ParseError: If input text fails to match the expected scheme pattern.
        """
        scheme = self._schemes[scheme_id]
        solver_id = self._solver_to_use[scheme_id]
        solver = self._solvers[solver_id]
        solution = solver.solve_scheme(text, scheme)
        if solution is None:
            raise ParseError(f"failed to parse text {text!r} as scheme {scheme_id!r}")
        return scheme.cls(*solution.source_pattern_tuple)

    @overload
    def convert_scheme_to_intermediate(
        self,
        source: str,
        scheme_id: str,
        validate: bool = ...,
        strict: Literal[True] = ...,
        solver_id: Literal[SupportedSolvers] | None = ...,
    ) -> PhonologyRepresentationT: ...

    @overload
    def convert_scheme_to_intermediate(
        self,
        source: str,
        scheme_id: str,
        validate: bool = ...,
        strict: Literal[False] = ...,
        solver_id: Literal[SupportedSolvers] | None = ...,
    ) -> PhonologyRepresentationT | None: ...

    def convert_scheme_to_intermediate(
        self,
        source: str,
        scheme_id: str,
        validate: bool = True,
        strict: bool = True,
        solver_id: Literal[SupportedSolvers] | None = None,
    ) -> PhonologyRepresentationT | None:
        """Converts scheme input into an intermediate phonological representation.

        Args:
            source: Source string in the target scheme format.
            scheme_id: Identifier of the registered scheme to convert from.
            validate: Whether to run phonotactic rules and roundtrip validation.
            strict: If True, raises exceptions on validation failure or missing solver
                solutions. If False, returns None instead.
            solver_id: Identifier of the solver to resolve source text into a solution.
                If `None`, picks the default solver from `self._solver_to_use`.

        Returns:
            An instantiated intermediate `PhonologyRepresentation` dataclass, or None
            if `strict=False` and conversion/validation fails.

        Raises:
            ValueError: If no valid solver solution exists and `strict=True`.
            PhonologicalError: If the input violates phonotactic rules and `strict=True`.
            NotSupportedError: If roundtrip validation fails and `strict=True`.
            KeyError: If `scheme_id` is not registered, or if `solver_id` is not in
                `self._solvers`.
        """
        return self._pipeline.convert_to_intermediate(
            source,
            scheme_id,
            validate,
            strict,
            solver_id,
        )

    @overload
    def convert_intermediate_to_scheme(
        self,
        source: str,
        scheme_id: str,
        validate: bool = ...,
        strict: Literal[True] = ...,
        solver_id: Literal[SupportedSolvers] | None = ...,
    ) -> SchemeRepresentation: ...

    @overload
    def convert_intermediate_to_scheme(
        self,
        source: str,
        scheme_id: str,
        validate: bool = ...,
        strict: Literal[False] = ...,
        solver_id: Literal[SupportedSolvers] | None = ...,
    ) -> SchemeRepresentation | None: ...

    def convert_intermediate_to_scheme(
        self,
        source: str,
        scheme_id: str,
        validate: bool = True,
        strict: bool = True,
        solver_id: Literal[SupportedSolvers] | None = None,
    ) -> SchemeRepresentation | None:
        """Converts intermediate phonological input into a scheme representation.

        Args:
            source: Source string in intermediate phonology format.
            scheme_id: Identifier of the registered target scheme to convert into.
            validate: Whether to run phonotactic rules and roundtrip validation.
            strict: If True, raises exceptions on validation failure or missing solver
                solutions. If False, returns None instead.
            solver_id: Identifier of the solver to resolve source text into a solution.
                If `None`, picks the default solver from `self._solver_to_use`.

        Returns:
            An instantiated target `SchemeRepresentation` dataclass, or None
            if `strict=False` and conversion/validation fails.

        Raises:
            ValueError: If no valid solver solution exists and `strict=True`.
            PhonologicalError: If the input violates phonotactic rules and `strict=True`.
            NotSupportedError: If roundtrip validation fails and `strict=True`.
            KeyError: If `scheme_id` is not registered, or if `solver_id` is not in
                `self._solvers`.
        """
        return self._pipeline.convert_to_scheme(
            source,
            scheme_id,
            validate,
            strict,
            solver_id,
        )

    @overload
    def convert_scheme_to_scheme(
        self,
        source: str,
        from_scheme_id: str,
        to_scheme_id: str,
        validate: bool = ...,
        strict: Literal[True] = ...,
    ) -> SchemeRepresentation: ...

    @overload
    def convert_scheme_to_scheme(
        self,
        source: str,
        from_scheme_id: str,
        to_scheme_id: str,
        validate: bool = ...,
        strict: Literal[False] = ...,
    ) -> SchemeRepresentation | None: ...

    def convert_scheme_to_scheme(
        self,
        source: str,
        from_scheme_id: str,
        to_scheme_id: str,
        validate: bool = True,
        strict: bool = True,
    ) -> SchemeRepresentation | None:
        """Converts a source scheme string directly to another registered scheme representation.

        Translates the source string through the intermediate phonological representation
        before converting to the target scheme.

        Args:
            source: Source text in the original scheme format.
            from_scheme_id: Identifier of the source scheme to convert from.
            to_scheme_id: Identifier of the target scheme to convert to.
            validate: Whether to run phonotactic rules and roundtrip validation.
            strict: If True, raises exceptions on validation failure or missing solver
                solutions. If False, returns None instead.

        Returns:
            An instantiated target `SchemeRepresentation` dataclass, or None
            if `strict=False` and conversion/validation fails.

        Raises:
            ValueError: If no valid solver solution exists and `strict=True`.
            PhonologicalError: If the input violates phonotactic rules and `strict=True`.
            NotSupportedError: If roundtrip validation fails and `strict=True`.
            KeyError: If `from_scheme_id` or `to_scheme_id` is not registered.
        """
        intermediate = self.convert_scheme_to_intermediate(
            source,
            from_scheme_id,
            validate,
            strict,
        )
        if intermediate is None:
            return None

        return self.convert_intermediate_to_scheme(
            str(intermediate),
            to_scheme_id,
            validate,
            strict,
        )
