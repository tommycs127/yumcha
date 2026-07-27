from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, fields
from enum import Enum
from functools import cached_property
from types import EllipsisType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .indexer import Indexer, IntermediateIndexer
    from .pattern_tuple import PatternTuple
    from .regexer import Regexer


type Pattern = str | EllipsisType
type PrePatternTuple = tuple[Pattern, ...]


class PhonologyRowDirective(Enum):
    REQUIRED = "*"
    OPTIONAL = "?"
    INVALID = "x"
    COMMENT = "#"


class SchemeRowDirective(Enum):
    BIDIRECTIONAL = "="  # Intermediate ⇔ Scheme (Both ways)
    FORWARD = ">"  # Intermediate ⇒ Scheme (Forward only)
    REVERSE = "<"  # Intermediate ⇐ Scheme (Reverse only)
    COMMENT = "#"


CharsetDict = dict[str, PhonologyRowDirective]


@dataclass(frozen=True)
class Representation(Iterable[str]):
    def __str__(self) -> str:
        return unicodedata.normalize("NFC", "".join(map(str, self)))

    def __iter__(self) -> Iterator[str]:
        for f in fields(self):
            yield getattr(self, f.name)

    def __getattr__(self, name: str) -> str:
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute {name!r}"
        )


@dataclass(frozen=True)
class Phonology[R_co: Representation]:
    id: str
    cls: type[R_co]
    fields: tuple[str, ...]
    charsets: tuple[set[str], ...]
    charset_dicts: tuple[CharsetDict, ...]
    invalid_patterns: tuple[PatternTuple, ...]
    regexer: Regexer

    @cached_property
    def charsets_classified(self) -> list[dict[PhonologyRowDirective, set[str]]]:
        return [
            {
                v: {k for k, val in charset_dict.items() if val == v}
                for v in charset_dict.values()
            }
            for charset_dict in self.charset_dicts
        ]

    @cached_property
    def charsets_sorted(self) -> list[list[str]]:
        return [sorted(s) for s in self.charsets]


@dataclass(frozen=True)
class Scheme[R_co: Representation]:
    id: str
    cls: type[R_co]
    intermediate_fields: tuple[str, ...]
    intermediate_indexer: IntermediateIndexer
    fields: dict[str, frozenset[int]]
    indexer: Indexer
    regexer: Regexer
    directions: tuple[SchemeRowDirective, ...]
