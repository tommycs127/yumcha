"""Directive enumerations for parsing and processing phonology and scheme row definitions."""

from enum import Enum

from ...core.primitives.directives import PhonologyDirective, SchemeDirective


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

    def to_core_directive(self) -> PhonologyDirective:
        """Converts the row directive to its corresponding core phonology directive.

        Returns:
            The matching `PhonologyDirective` enum member.

        Raises:
            KeyError: If there is no corresponding `PhonologyDirective` with the same name.
        """
        return PhonologyDirective[self.name]


class SchemeRowDirective(Enum):
    """Directives specifying directional mapping pattern tuples between Intermediate and Scheme forms.

    Attributes:
        BIDIRECTIONAL: Mapping applies in both directions (`=`).
        FORWARD: Mapping applies only from Intermediate to Scheme (`>`).
        REVERSE: Mapping applies only from Scheme to Intermediate (`<`).
        INVALID: Marks a row as explicitly invalid (`x`).
        COMMENT: Designates a row as a comment (`#`).
    """

    BIDIRECTIONAL = "="
    FORWARD = ">"
    REVERSE = "<"
    INVALID = "x"
    COMMENT = "#"

    def to_core_directive(self) -> SchemeDirective:
        """Converts the row directive to its corresponding core scheme directive.

        Returns:
            The matching `SchemeDirective` enum member.

        Raises:
            KeyError: If there is no corresponding `SchemeDirective` with the same name.
        """
        return SchemeDirective[self.name]
