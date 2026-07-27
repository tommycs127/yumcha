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
from .validator import Validator


class Language[PR: Representation, SR: Representation]:
    phonology: Phonology[PR]

    def __init__(self, phonology: Phonology[PR]) -> None:
        self.phonology = phonology
        self._schemes: dict[str, Scheme[SR]] = {}

    @property
    def schemes(self) -> MappingProxyType[str, Scheme[SR]]:
        return MappingProxyType(self._schemes)

    def add_scheme(self, scheme: str | Traversable | Scheme[SR]) -> None:
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
        return self._schemes.pop(scheme_id)

    def parse_as_intermediate(self, text: str) -> PR:
        return self.phonology.cls(*self.phonology.regexer.tokenize(text))

    def parse_as_scheme(self, scheme_id: str, text: str) -> SR:
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
        validate: bool = False,
        strict: bool = True,
    ) -> PatternTuple | None:
        scheme = self._schemes[scheme_id]

        result, used_indexes = self._find_best_result(
            scheme, pattern_tuple, as_, strict
        )

        if result is None:
            return None

        if validate:
            args = (self, scheme, result, used_indexes, as_)

            if not strict:
                if not Validator.validate(*args, strict=False):
                    return None
            else:
                try:
                    Validator.validate(*args)
                except Exception as e:
                    raise ValueError(
                        f"failed to convert pattern tuple {pattern_tuple} "
                        f"using scheme '{scheme_id}': {e}"
                    ) from e

        return result
