"""Scheme facade models and field indexing utilities.

Provides high-level data models defining transcription schemes and orthographic mapping strategies
for phonological representations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cluster_canonicalizer import ClusterCanonicalizer
    from ..indexer import Indexer
    from ..models.representation import Representation
    from ..primitives.directives import SchemeDirective


@dataclass(frozen=True)
class Scheme[RepresentationT_co: Representation]:
    """Defines a transcription scheme or orthographic mapping strategy for a `Phonology`.

    Attributes:
        id: Unique identifier for this scheme.
        cls: The concrete `Representation` subclass type used.
        intermediate_fields: Mapping of intermediate field names to their corresponding slot indices.
        intermediate_indexer: Indexed pattern_tuples and invalid mask lookup tables for intermediate fields.
        fields: Mapping of scheme field names to their corresponding slot indices.
        indexer: Indexed pattern_tuples and invalid mask lookup tables for scheme fields.
        directions: Conversion directional directives (bidirectional, forward, reverse) per row.
        canonicalizer: The cluster canonicalizer instance used to normalize combining mark sequences.
    """

    id: str
    cls: type[RepresentationT_co]
    intermediate_fields: MappingProxyType[str, frozenset[int]]
    intermediate_indexer: Indexer
    fields: MappingProxyType[str, frozenset[int]]
    indexer: Indexer
    directions: tuple[SchemeDirective, ...]
    canonicalizer: ClusterCanonicalizer

    def __post_init__(self) -> None:
        """Pre-computes cached properties upon object initialization."""
        if self.are_field_indexes_sequential:
            _ = self.compiled_re_pattern

    @cached_property
    def are_field_indexes_sequential(self) -> bool:
        """Determines whether intermediate field indices are contiguous and sequentially ordered.

        Returns:
            `True` if all field index ranges are contiguous and non-overlapping in sequence order,
            otherwise `False`.

        Raises:
            ValueError: If any field in `fields` maps to an empty set of intermediate indices.
        """
        last_max_intermediate_index = -1
        fields = self.fields

        for field, intermediate_indexes in fields.items():
            if not intermediate_indexes:
                raise ValueError(
                    "unknown relation to intermediate representation "
                    + f"at field {field!r} (likely a misconfigured scheme)"
                )
            min_idx = min(intermediate_indexes)
            max_idx = max(intermediate_indexes)
            if (max_idx - min_idx + 1) != len(intermediate_indexes):
                return False
            if min_idx < last_max_intermediate_index:
                return False
            last_max_intermediate_index = max_idx

        return True

    @cached_property
    def re_pattern(self) -> str:
        """Compiles a regex group pattern matching valid feature combinations across slots.

        Returns:
            A regular expression string capturing all character sets in field order.

        Raises:
            ValueError: If field indexes are non-sequential.
        """
        if not self.are_field_indexes_sequential:
            raise ValueError(f"field indexes of scheme {self.id!r} are non-sequential.")

        groups: list[str] = []
        pattern_masks_by_fields = self.indexer.pattern_masks_by_fields
        for patterns in pattern_masks_by_fields:
            valid_patterns = [re.escape(p) for p in patterns if isinstance(p, str)]
            if not valid_patterns:
                groups.append("()")
            elif len(valid_patterns) == 1:
                groups.append(f"({valid_patterns[0]})")
            else:
                valid_patterns.sort(key=len, reverse=True)
                groups.append(f"({'|'.join(valid_patterns)})")

        return "".join(groups)

    @cached_property
    def compiled_re_pattern(self) -> re.Pattern[str]:
        """Compiles the regex string pattern into a reusable `re.Pattern` object.

        Returns:
            A compiled regular expression pattern object.

        Raises:
            ValueError: If field indexes are non-sequential.
        """
        return re.compile(self.re_pattern)
