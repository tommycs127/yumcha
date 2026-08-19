"""Phonology facade models and character group compilation.

Provides high-level data models representing complete phonological grammar specifications,
along with utilities to classify character sets by directive and compile regular expression patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cluster_canonicalizer import ClusterCanonicalizer
    from ..models.representation import Representation
    from ..primitives.directives import PhonologyDirective, PhonologyDirectiveMap
    from ..primitives.pattern_tuple import PatternTuple


@dataclass(frozen=True)
class Phonology[Representation_co: Representation]:
    """Represents a complete phonological grammar specification and its validation rules.

    Attributes:
        id: Unique string identifier for this phonology definition.
        cls: The `Representation` subclass type backing this phonology's feature structures.
        fields: Tuple of field/feature names matching `cls`.
        charsets: Sets of valid characters partitioned by feature position.
        phonology_directive_maps: Directives dictating character validity constraints per feature slot.
        invalid_pattern_tuples: Tuples of wildcard/feature patterns that are illegal in this phonology.
        canonicalizer: The cluster canonicalizer instance used to normalize combining mark sequences.
    """

    id: str
    cls: type[Representation_co]
    fields: tuple[str, ...]
    charsets: tuple[set[str], ...]
    phonology_directive_maps: tuple[PhonologyDirectiveMap, ...]
    invalid_pattern_tuples: tuple[PatternTuple, ...]
    canonicalizer: ClusterCanonicalizer

    def __post_init__(self) -> None:
        """Pre-computes cached properties upon object initialization."""
        _ = self.charsets_classified
        _ = self.charsets_sorted
        _ = self.compiled_re_pattern

    @cached_property
    def charsets_classified(self) -> list[dict[PhonologyDirective, set[str]]]:
        """Groups characters in each slot by their associated `PhonologyDirective`.

        Returns:
            A list (one per slot) of dictionaries mapping each directive
            to the set of characters assigned to it.
        """
        return [
            {
                v: {k for k, val in charset_dict.items() if val == v}
                for v in charset_dict.values()
            }
            for charset_dict in self.phonology_directive_maps
        ]

    @cached_property
    def charsets_sorted(self) -> list[list[str]]:
        """Provides sorted lists of valid characters for each phonological slot.

        Returns:
            A list containing sorted character lists for every feature position.
        """
        return [sorted(s) for s in self.charsets]

    @cached_property
    def re_pattern(self) -> str:
        """Compiles a regex group pattern matching valid feature combinations across slots.

        Returns:
            A regular expression string capturing all character sets in field order.
        """
        return "".join(
            f"({'|'.join(re.escape(c) for c in sorted(charset, key=len, reverse=True))})"
            for charset in self.charsets
        )

    @cached_property
    def compiled_re_pattern(self) -> re.Pattern[str]:
        """Compiles the regex string pattern into a reusable `re.Pattern` object.

        Returns:
            A compiled regular expression pattern object.
        """
        return re.compile(self.re_pattern)
