"""Loader functions for compiling phonology specifications and scheme mappings."""

from __future__ import annotations

from dataclasses import make_dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from ..core.cluster_canonicalizer import ClusterCanonicalizer
from ..core.facades.phonology import Phonology
from ..core.facades.scheme import Scheme
from ..core.models.representation import (
    PhonologyRepresentation,
    SchemeRepresentation,
)
from ..core.primitives.directives import SchemeDirective
from ..core.registered_pattern_tuples import RegisteredPatternTupleWithInvalidMasks

if TYPE_CHECKING:
    from ..core.models.specs import PhonologyData, SchemeData


def load_phonology(
    phonology_data: PhonologyData,
) -> Phonology[PhonologyRepresentation]:
    """Loads and compiles a phonology specification from a TSV resource.

    Parses table data to build character sets, validation rules, regex tokenization,
    and a dynamically generated `Representation` subclass representing language phone
    structures.

    Args:
        phonology_data: A `PhonologyData` container.

    Returns:
        A compiled `Phonology` instance containing character sets, regex tokenizers,
        invalid pattern tuples, and dynamic representation classes.

    Raises:
        ValueError: If `lang_id` is empty or not a valid Python identifier.
    """
    (
        id,
        fields,
        charsets,
        char_directives,
        invalid_pattern_tuples,
    ) = phonology_data.to_tuple()

    canonicalizer = ClusterCanonicalizer()
    canonicalizer.learn(charsets)

    class_name = "".join(s.capitalize() for s in id.split("_"))
    class_fields = [(f, str) for f in fields]

    class_: type[PhonologyRepresentation] = make_dataclass(
        cls_name=class_name,
        fields=class_fields,
        frozen=True,
        bases=(PhonologyRepresentation,),
    )

    return Phonology(
        id,
        class_,
        fields,
        tuple(charsets),
        tuple(char_directives),
        tuple(invalid_pattern_tuples),
        canonicalizer,
    )


def load_scheme(
    scheme_data: SchemeData,
) -> Scheme[SchemeRepresentation]:
    """Loads and compiles a orthographic/romanization scheme mapping from a TSV resource.

    Parses mapping definitions to construct forward and reverse indexers, regex pattern
    matchers, and a dynamically generated `Representation` subclass for the scheme's field structure.

    Args:
        scheme_data: A `SchemeData` container.

    Returns:
        A loaded `Scheme` instance.

    Raises:
        ValueError: If `scheme_id` is not a valid Python identifier.
    """

    (
        id,
        directions,
        intermediate_fields,
        intermediate_pattern_tuples,
        fields,
        pattern_tuples,
        invalid_pattern_tuples,
    ) = scheme_data.to_tuple()

    intermediate_registrants = RegisteredPatternTupleWithInvalidMasks()
    intermediate_registrants.load(
        intermediate_pattern_tuples,
        directions,
        {
            SchemeDirective.BIDIRECTIONAL,
            SchemeDirective.FORWARD,
        },
    )

    registrants = RegisteredPatternTupleWithInvalidMasks()
    registrants.load(
        pattern_tuples,
        directions,
        {
            SchemeDirective.BIDIRECTIONAL,
            SchemeDirective.REVERSE,
        },
    )
    registrants.build_invalid_masks(invalid_pattern_tuples)

    canonicalizer = ClusterCanonicalizer()
    canonicalizer.learn(registrants.charsets)

    class_name = "".join(s.capitalize() for s in id.split("_"))
    cls_fields = [(f, str) for f in scheme_data.fields]

    cls: type[SchemeRepresentation] = make_dataclass(
        cls_name=class_name,
        fields=cls_fields,
        frozen=True,
        bases=(SchemeRepresentation,),
    )

    return Scheme[SchemeRepresentation](
        id,
        cls,
        MappingProxyType(intermediate_fields),
        intermediate_registrants,
        MappingProxyType(fields),
        registrants,
        directions,
        canonicalizer,
    )
