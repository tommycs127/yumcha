from collections.abc import Iterable
from importlib.resources.abc import Traversable
from pathlib import Path
from types import MappingProxyType
from typing import Literal, overload

from .core.exceptions import (
    AmbiguousMatchError,
    NoMatchError,
    ParseError,
    ReadError,
)
from .core.merger import merge
from .core.models import (
    Phonology,
    PhonologyRowDirective,
    Representation,
    Scheme,
)
from .core.pattern_tuple import PatternTuple
from .core.tsv.loader import load_scheme
from .syllable_table import ProgressBarWrapper, SyllableTable
from .validator import validate as validate_converted


class Language[PR: Representation, SR: Representation]:
    """Coordinates phonological representations and orthographic/romanization schemes.

    Provides high-level APIs for converting phoneme representations to/from registered
    schemes, cross-converting between schemes, running validations, and generating
    combinatorial syllable tables.

    Attributes:
        phonology: The core `Phonology` instance managing intermediate representations.
    """

    phonology: Phonology[PR]

    def __init__(self, phonology: Phonology[PR]) -> None:
        """Initializes a Language instance with a phonology spec.

        Args:
            phonology: `Phonology` instance containing character sets and phonotactic rules.
        """
        self.phonology = phonology
        self._schemes: dict[str, Scheme[SR]] = {}

    @property
    def schemes(self) -> MappingProxyType[str, Scheme[SR]]:
        """Gets a read-only mapping view of registered scheme IDs to `Scheme` instances.

        Returns:
            A `MappingProxyType` dictionary mapping scheme names to `Scheme` objects.
        """
        return MappingProxyType(self._schemes)

    def add_scheme(self, scheme: str | Traversable | Scheme[SR]) -> None:
        """Loads, validates, and registers a scheme mapping.

        Args:
            scheme: File path string, `Traversable` resource, or pre-built `Scheme` object.

        Raises:
            ReadError: If the scheme file cannot be opened or read.
            ParseError: If the scheme definition is malformed.
            ValueError: If character sets in the scheme conflict with phonology requirements.
        """
        if not isinstance(scheme, Scheme):
            resource = Path(scheme) if isinstance(scheme, str) else scheme

            try:
                scheme = load_scheme(resource)
            except OSError as e:
                raise ReadError(resource.name, cause=e) from e
            except ValueError as e:
                raise ParseError(resource.name, cause=e) from e

        self.validate_scheme(scheme)
        scheme.intermediate_indexer.build_invalid_masks(self.phonology.invalid_patterns)
        self._schemes[scheme.id] = scheme

    def validate_scheme(self, scheme: Scheme[SR]) -> None:
        """Validates that a scheme covers all required phonology character sets.

        Args:
            scheme: `Scheme` instance to validate against the active phonology.

        Raises:
            ValueError: If phonemes required by phonology are missing in the scheme,
                or if redundant phonemes are present in the scheme.
        """
        for idx, phonology_charset in enumerate(self.phonology.charset_dicts):
            phonology_required = self.phonology.charsets_classified[idx][
                PhonologyRowDirective.REQUIRED
            ]
            scheme_charset = scheme.intermediate_indexer.charsets[idx]

            if missing_charset := (phonology_required - scheme_charset):
                raise ValueError(
                    f"missing phonemes for {self.phonology.fields[idx]}: "
                    f"add {sorted(missing_charset)}"
                )

            if redundant_charset := (scheme_charset - set(phonology_charset)):
                raise ValueError(
                    f"redundant phonemes for {self.phonology.fields[idx]}: "
                    f"remove {sorted(redundant_charset)}"
                )

    def pop_scheme(self, scheme_id: str) -> Scheme[SR]:
        """Removes and returns a registered scheme by ID.

        Args:
            scheme_id: Identifier of the scheme to unregister.

        Returns:
            The removed `Scheme` instance.

        Raises:
            KeyError: If `scheme_id` is not registered.
        """
        return self._schemes.pop(scheme_id)

    def parse_as_intermediate(self, text: str) -> PR:
        """Tokenizes text into a phonological intermediate `Representation`.

        Args:
            text: Raw input string to tokenize.

        Returns:
            An instantiated intermediate `Representation` dataclass.
        """
        return self.phonology.cls(*self.phonology.regexer.tokenize(text))

    def parse_as_scheme(self, scheme_id: str, text: str) -> SR:
        """Tokenizes text into a target scheme `Representation`.

        Args:
            scheme_id: Identifier of the target registered scheme.
            text: Raw scheme input string to tokenize.

        Returns:
            An instantiated target scheme `Representation` dataclass.
        """
        scheme = self._schemes[scheme_id]
        return scheme.cls(*scheme.regexer.tokenize(text))

    @overload
    def to_intermediate(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        validate: bool = ...,
        strict: Literal[True] = ...,
    ) -> PR: ...

    @overload
    def to_intermediate(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        validate: bool = ...,
        strict: Literal[False] = ...,
    ) -> PR | None: ...

    def to_intermediate(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        validate: bool = True,
        strict: bool = True,
    ) -> PR | None:
        """Converts scheme input into an intermediate phonological representation.

        Args:
            scheme_id: Source scheme identifier.
            source: Raw text string or iterable of field components.
            validate: Whether to run phonotactic and roundtrip validation checks.
                Defaults to `True`.
            strict: If `True`, raises an error on failure; if `False`, returns `None`.
                Defaults to `True`.

        Returns:
            The converted phonological intermediate `Representation`, or `None` if
            conversion failed and `strict=False`.
        """
        iterable = (
            self.parse_as_scheme(scheme_id, source)
            if isinstance(source, str)
            else source
        )
        pattern_tuple = (
            iterable if isinstance(iterable, PatternTuple) else PatternTuple(iterable)
        )
        result = self._convert_representation(
            scheme_id, pattern_tuple, "scheme", validate, strict
        )
        return self.phonology.cls(*result) if result else None

    @overload
    def to_scheme(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        validate: bool = ...,
        strict: Literal[True] = ...,
    ) -> SR: ...

    @overload
    def to_scheme(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        validate: bool = ...,
        strict: Literal[False] = ...,
    ) -> SR | None: ...

    def to_scheme(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        validate: bool = True,
        strict: bool = True,
    ) -> SR | None:
        """Converts intermediate phonological input into a scheme representation.

        Args:
            scheme_id: Target scheme identifier.
            source: Raw text string or iterable of field components.
            validate: Whether to run phonotactic and roundtrip validation checks.
                Defaults to `True`.
            strict: If `True`, raises an error on failure; if `False`, returns `None`.
                Defaults to `True`.

        Returns:
            The target scheme `Representation`, or `None` if conversion failed and
            `strict=False`.
        """
        iterable = (
            self.parse_as_intermediate(source) if isinstance(source, str) else source
        )
        pattern_tuple = (
            iterable if isinstance(iterable, PatternTuple) else PatternTuple(iterable)
        )
        result = self._convert_representation(
            scheme_id, pattern_tuple, "intermediate", validate, strict
        )
        return self._schemes[scheme_id].cls(*result) if result else None

    @overload
    def scheme_to_scheme(
        self,
        from_scheme_id: str,
        to_scheme_id: str,
        source: str | Iterable[str],
        validate: bool = ...,
        strict: Literal[True] = ...,
    ) -> SR: ...

    @overload
    def scheme_to_scheme(
        self,
        from_scheme_id: str,
        to_scheme_id: str,
        source: str | Iterable[str],
        validate: bool = ...,
        strict: Literal[False] = ...,
    ) -> SR | None: ...

    def scheme_to_scheme(
        self,
        from_scheme_id: str,
        to_scheme_id: str,
        source: str | Iterable[str],
        validate: bool = True,
        strict: bool = True,
    ) -> SR | None:
        """Converts representation directly from one scheme to another.

        Translates source scheme inputs through intermediate representation to the target scheme.

        Args:
            from_scheme_id: Source scheme identifier.
            to_scheme_id: Target scheme identifier.
            source: Raw text string or iterable of source field components.
            validate: Whether to run phonotactic and roundtrip validation checks.
                Defaults to `True`.
            strict: If `True`, raises an error on failure; if `False`, returns `None`.
                Defaults to `True`.

        Returns:
            The target scheme `Representation`, or `None` if conversion failed and
            `strict=False`.
        """
        parsed_from_scheme = (
            self.parse_as_scheme(from_scheme_id, source)
            if isinstance(source, str)
            else source
        )
        intermediate = self.to_intermediate(
            from_scheme_id, parsed_from_scheme, validate, strict
        )
        if intermediate:
            to_scheme = self.to_scheme(to_scheme_id, intermediate, validate, strict)
        else:
            return None

        if to_scheme:
            return self._schemes[to_scheme_id].cls(*to_scheme)
        return None

    def validate(
        self,
        scheme_id: str,
        source: str | Iterable[str],
        as_: Literal["intermediate", "scheme"] = "intermediate",
    ) -> None:
        """Validates that an input representation converts cleanly and passes rules.

        Args:
            scheme_id: Target scheme identifier.
            source: Raw text string or iterable of field components.
            as_: Mode context specifying whether `source` represents an "intermediate"
                or target "scheme" input. Defaults to "intermediate".

        Raises:
            ValueError: If validation checks fail.
        """
        iterable = (
            (
                self.parse_as_intermediate(source)
                if as_ == "intermediate"
                else self.parse_as_scheme(scheme_id, source)
            )
            if isinstance(source, str)
            else source
        )
        pattern_tuple = (
            iterable if isinstance(iterable, PatternTuple) else PatternTuple(iterable)
        )
        self._convert_representation(scheme_id, pattern_tuple, as_, True)

    def syllable_table(
        self,
        progress_bar: ProgressBarWrapper | None = None,
    ) -> SyllableTable:
        """Instantiates a `SyllableTable` generator for combinatorial matrix analysis.

        Args:
            progress_bar: Optional callable conforming to `ProgressBarWrapper` to wrap iteration.

        Returns:
            A configured `SyllableTable` iterator instance.
        """
        return SyllableTable(self, progress_bar)

    @overload
    def _get_best_match(
        self,
        scheme: Scheme[SR],
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"] = "intermediate",
        strict: Literal[True] = ...,
    ) -> tuple[tuple[int, ...], PatternTuple]: ...

    @overload
    def _get_best_match(
        self,
        scheme: Scheme[SR],
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"] = "intermediate",
        strict: Literal[False] = ...,
    ) -> tuple[tuple[int, ...], PatternTuple | None]: ...

    def _get_best_match(
        self,
        scheme: Scheme[SR],
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"] = "intermediate",
        strict: bool = True,
    ) -> tuple[tuple[int, ...], PatternTuple | None]:
        """Finds the optimal indexing match for a pattern tuple in the target indexer.

        Args:
            scheme: Target `Scheme` object.
            pattern_tuple: Pattern tuple to search for.
            as_: Lookup mode, either "intermediate" or "scheme". Defaults to "intermediate".
            strict: If `True`, raises match errors; if `False`, returns empty match tuples.

        Returns:
            A tuple containing:
                - `matched_indexes`: Tuple of matching row indices.
                - `matched_tuple`: Best matched `PatternTuple` or `None`.

        Raises:
            NoMatchError: If no candidate match is found and `strict=True`.
            AmbiguousMatchError: If multiple conflicting matches are found and `strict=True`.
        """
        indexer = (
            scheme.intermediate_indexer if as_ == "intermediate" else scheme.indexer
        )
        matches = indexer.find_matches(pattern_tuple)
        best_matches = merge(matches)

        if len(best_matches) == 1:
            return best_matches[0]

        elif len(best_matches) < 1:
            if not strict:
                return (), None
            raise NoMatchError(
                f"invalid pattern tuple {pattern_tuple} (as {as_}) for scheme '{scheme}'"
            )

        else:
            if not strict:
                return (), None

            formatted_matches = []

            for match in best_matches:
                line_nos = tuple(
                    idx + 2 for idx in match[0]
                )  # adds 2 to offset 0-indexing and skip the header line
                formatted_matches.append(f"- {line_nos}")

            matches_str = "\n".join(formatted_matches)

            raise AmbiguousMatchError(
                f"Ambiguous pattern tuple {pattern_tuple} for scheme '{scheme}'.\n"
                f"Possible matches found at TSV line numbers:\n{matches_str}\n"
                "Review the scheme design to resolve this ambiguity."
            )

    @overload
    def _find_best_result(
        self,
        scheme: Scheme[SR],
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"],
        strict: Literal[True] = ...,
    ) -> tuple[PatternTuple, set[int]]: ...

    @overload
    def _find_best_result(
        self,
        scheme: Scheme[SR],
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"],
        strict: Literal[False] = ...,
    ) -> tuple[PatternTuple | None, set[int]]: ...

    def _find_best_result(
        self,
        scheme: Scheme[SR],
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"],
        strict: bool = True,
    ) -> tuple[PatternTuple | None, set[int]]:
        """Merges matching scheme rows into a complete target pattern tuple.

        Args:
            scheme: Target `Scheme` object.
            pattern_tuple: Source pattern tuple to match.
            as_: Mode specifying input perspective ("intermediate" or "scheme").
            strict: If `True`, raises `NoMatchError` on incomplete merges;
                if `False`, returns `None`.

        Returns:
            A tuple containing:
                - `merged_result`: Merged complete `PatternTuple`, or `None`.
                - `used_indexes`: Set of scheme row indices used during the merge.

        Raises:
            NoMatchError: If merged pattern is incomplete and `strict=True`.
        """
        best_match_indexes, _ = self._get_best_match(scheme, pattern_tuple, as_, strict)

        if not best_match_indexes:
            return None, set()

        target_indexer = (
            scheme.intermediate_indexer if as_ == "scheme" else scheme.indexer
        )

        result = PatternTuple((...,)) * target_indexer.pattern_tuple_length
        used_indexes: set[int] = set()

        for idx in best_match_indexes:
            try:
                result_new = result.merge(target_indexer.pattern_tuples_raw[idx])

                # No need to add index if nothing is changed in the merged result
                if result_new.occupancy == result.occupancy:
                    continue

                result = result_new
                used_indexes.add(idx)
            except ValueError:
                # Cannot merge because the target tuples
                # have different components in the same slot
                continue  # Skip to try the rest

        if not result.is_complete():
            if not strict:
                return None, used_indexes
            raise NoMatchError(
                f"invalid pattern tuple {pattern_tuple} for scheme '{scheme.id}'.\n"
                f"Review the {'intermediate' if as_ == 'scheme' else 'scheme'} columns "
                "for potential merge conflicts."
            )

        return result, used_indexes

    @overload
    def _convert_representation(
        self,
        scheme_id: str,
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"],
        validate: bool = ...,
        strict: Literal[True] = ...,
    ) -> PatternTuple: ...

    @overload
    def _convert_representation(
        self,
        scheme_id: str,
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"],
        validate: bool = ...,
        strict: Literal[False] = ...,
    ) -> PatternTuple | None: ...

    def _convert_representation(
        self,
        scheme_id: str,
        pattern_tuple: PatternTuple,
        as_: Literal["intermediate", "scheme"],
        validate: bool = True,
        strict: bool = True,
    ) -> PatternTuple | None:
        """Executes low-level conversion logic and validation.

        Args:
            scheme_id: Identifier of target scheme.
            pattern_tuple: Input `PatternTuple` to convert.
            as_: Mode specifying input type ("intermediate" or "scheme").
            validate: Whether to run validator suite. Defaults to `True`.
            strict: If `True`, raises `ValueError` on failure; if `False`, returns `None`.

        Returns:
            Converted `PatternTuple`, or `None` if conversion or validation fails under `strict=False`.

        Raises:
            ValueError: If conversion or validation fails when `strict=True`.
        """
        scheme = self._schemes[scheme_id]

        result, used_indexes = self._find_best_result(
            scheme, pattern_tuple, as_, strict
        )

        if result is None:
            return None

        if validate:
            args = (self, scheme, result, used_indexes, as_)

            if not strict:
                if not validate_converted(*args, strict=False):
                    return None
            else:
                try:
                    validate_converted(*args)
                except Exception as e:
                    raise ValueError(
                        f"failed to convert pattern tuple {pattern_tuple} "
                        f"using scheme '{scheme_id}': {e}"
                    ) from e

        return result
