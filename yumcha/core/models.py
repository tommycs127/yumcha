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
"""Type alias representing either a character pattern string or an wildcard (`...`)."""

type PrePatternTuple = tuple[Pattern, ...]
"""Type alias for raw un-parsed tuples containing string patterns or wildcards."""


class PhonologyRowDirective(Enum):
    """Directives controlling how individual phonological rows are validated.

    Attributes:
        REQUIRED: Indicates a row that must be present (`*`).
        OPTIONAL: Indicates a row that is optional (`?`).
        INVALID: Marks a row as explicitly invalid (`x`).
        COMMENT: Designates a row as a comment to be ignored (`#`).
    """

    REQUIRED = "*"
    OPTIONAL = "?"
    INVALID = "x"
    COMMENT = "#"


class SchemeRowDirective(Enum):
    """Directives specifying directional mapping constraints between Intermediate and Scheme forms.

    Attributes:
        BIDIRECTIONAL: Mapping applies in both directions (`=`).
        FORWARD: Mapping applies only from Intermediate to Scheme (`>`).
        REVERSE: Mapping applies only from Scheme to Intermediate (`<`).
        COMMENT: Designates a row as a comment (`#`).
    """

    BIDIRECTIONAL = "="
    FORWARD = ">"
    REVERSE = "<"
    COMMENT = "#"


type CharsetDict = dict[str, PhonologyRowDirective]
"""Type alias mapping character strings to their corresponding phonological validation directives."""


@dataclass(frozen=True)
class Representation(Iterable[str]):
    """An abstract immutable container representing feature structures.

    Subclasses define fields corresponding to individual features or phonological slots.
    Iterating over a `Representation` yields the value of each field in definition order.
    """

    def __str__(self) -> str:
        """Returns the NFC-normalized string composed by joining all field values.

        Returns:
            A single Unicode string representing the complete phone or sequence.
        """
        return unicodedata.normalize("NFC", "".join(map(str, self)))

    def __iter__(self) -> Iterator[str]:
        """Yields each field value in the order they were defined on the dataclass.

        Yields:
            The string value of each field attribute sequentially.
        """
        for f in fields(self):
            yield getattr(self, f.name)

    def __getattr__(self, name: str) -> str:
        """Handles lookup attempts for non-existent attributes.

        Args:
            name: The name of the attribute being accessed.

        Raises:
            AttributeError: Always raised with a formatted message indicating the missing attribute.
        """
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute {name!r}"
        )


@dataclass(frozen=True)
class Phonology[R_co: Representation]:
    """Represents a complete phonological grammar specification and its validation rules.

    Attributes:
        id: Unique string identifier for this phonology definition.
        cls: The `Representation` subclass type backing this phonology's feature structures.
        fields: Tuple of field/feature names matching `cls`.
        charsets: Sets of valid characters partitioned by feature position.
        charset_dicts: Directives dictating character validity constraints per feature slot.
        invalid_patterns: Tuples of wildcard/feature patterns that are illegal in this phonology.
        regexer: Compiled regex helper used for fast phonological pattern matching.
    """

    id: str
    cls: type[R_co]
    fields: tuple[str, ...]
    charsets: tuple[set[str], ...]
    charset_dicts: tuple[CharsetDict, ...]
    invalid_patterns: tuple[PatternTuple, ...]
    regexer: Regexer

    @cached_property
    def charsets_classified(self) -> list[dict[PhonologyRowDirective, set[str]]]:
        """Groups characters in each slot by their associated `PhonologyRowDirective`.

        Returns:
            A list (one per slot) of dictionaries mapping each directive
            to the set of characters assigned to it.
        """
        return [
            {
                v: {k for k, val in charset_dict.items() if val == v}
                for v in charset_dict.values()
            }
            for charset_dict in self.charset_dicts
        ]

    @cached_property
    def charsets_sorted(self) -> list[list[str]]:
        """Provides sorted lists of valid characters for each phonological slot.

        Returns:
            A list containing sorted character lists for every feature position.
        """
        return [sorted(s) for s in self.charsets]


@dataclass(frozen=True)
class Scheme[R_co: Representation]:
    """Defines a transcription scheme or orthographic mapping strategy for a `Phonology`.

    Attributes:
        id: Unique identifier for this scheme.
        cls: The concrete `Representation` subclass type used.
        intermediate_fields: Names of fields present in the intermediate phonological stage.
        intermediate_indexer: Indexer managing lookups for intermediate representations.
        fields: Mapping of scheme field names to their corresponding slot indices.
        indexer: Primary indexer managing lookups for scheme representations.
        regexer: Compiled regex helper for processing scheme text.
        directions: Conversion directional directives (bidirectional, forward, reverse) per row.
    """

    id: str
    cls: type[R_co]
    intermediate_fields: tuple[str, ...]
    intermediate_indexer: IntermediateIndexer
    fields: dict[str, frozenset[int]]
    indexer: Indexer
    regexer: Regexer
    directions: tuple[SchemeRowDirective, ...]
