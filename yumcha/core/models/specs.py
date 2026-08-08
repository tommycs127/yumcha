"""Data specification containers for phonological and scheme definitions.

Provides structured dataclasses holding parsed header fields, character sets,
pattern_tuples, and operational directives.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..primitives.directives import PhonologyDirectiveMap, SchemeDirective
    from ..primitives.pattern_tuple import PatternTuple


@dataclass(frozen=True)
class PhonologyData:
    """Container holding parsed phonology data.

    Attributes:
        id: The identifier of the phonology system.
        fields: Tuple of header field names.
        charsets: Tuple of character sets (one set per field position).
        char_directives: Tuple of dictionaries mapping characters to their directives per field position.
        invalid_pattern_tuples: Tuple of pattern tuples representing invalid feature patterns or wildcards.
    """

    id: str
    fields: tuple[str, ...]
    charsets: tuple[set[str], ...]
    char_directives: tuple[PhonologyDirectiveMap, ...]
    invalid_pattern_tuples: tuple[PatternTuple, ...]


@dataclass(frozen=True)
class SchemeData:
    """Container holding parsed schema data.

    Attributes:
        id: The identifier of the scheme.
        directions: Tuple of row directives across data rows.
        intermediate_fields: Map of intermediate field names to sets of field index positions.
        intermediate_pattern_tuples: Collection of parsed intermediate pattern pattern tuples per row.
        fields: Map of scheme field names to sets of field index positions.
        pattern_tuples: Collection of parsed scheme pattern pattern tuples per row.
        invalid_pattern_tuples: Collection of pattern tuples representing invalid feature patterns.
    """

    id: str
    directions: tuple[SchemeDirective, ...]
    intermediate_fields: dict[str, frozenset[int]]
    intermediate_pattern_tuples: tuple[PatternTuple, ...]
    fields: dict[str, frozenset[int]]
    pattern_tuples: tuple[PatternTuple, ...]
    invalid_pattern_tuples: tuple[PatternTuple, ...]
