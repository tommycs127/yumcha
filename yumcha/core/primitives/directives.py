"""Directive enumerations and type maps for phonological validation and mapping.

Defines control directives used to specify phonological constraints and
directional mapping rules between intermediate and scheme representations.
"""

from enum import Enum


class PhonologyDirective(Enum):
    """Directives controlling how individual phonological pattern tuples are validated.

    Attributes:
        REQUIRED: Indicates a pattern tuple that must be present (`*`).
        OPTIONAL: Indicates a pattern tuple that is optional (`?`).
        INVALID: Marks a pattern tuple as explicitly invalid (`x`).
    """

    REQUIRED = "*"
    OPTIONAL = "?"
    INVALID = "x"


type PhonologyDirectiveMap = dict[str, PhonologyDirective]
"""Type alias representing a mapping from string identifiers to phonological directives."""


class SchemeDirective(Enum):
    """Directives specifying directional mapping pattern tuples between Intermediate and Scheme forms.

    Attributes:
        BIDIRECTIONAL: Mapping applies in both directions (`=`).
        FORWARD: Mapping applies only from Intermediate to Scheme (`>`).
        REVERSE: Mapping applies only from Scheme to Intermediate (`<`).
        INVALID_FORWARD: Marks the Intermediate side of a row as explicitly invalid (`x>`).
            The Scheme side is not processed, but serves as a reference for why the row exists.
        INVALID_REVERSE: Marks the Scheme side of a row as explicitly invalid (`x<`).
            The Intermediate side is not processed, but serves as a reference for why the row exists.
    """

    BIDIRECTIONAL = "="
    FORWARD = ">"
    REVERSE = "<"
    INVALID_FORWARD = "x>"
    INVALID_REVERSE = "x<"
