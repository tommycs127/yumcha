"""Exception hierarchy for phonological rule processing and scheme execution errors.

Provides custom exception classes to handle domain-specific errors such as rule violations,
unresolved pattern queries, and unsupported scheme operations.
"""


class CoreError(Exception):
    """Base exception for all phonological and scheme processing errors."""


class SchemeError(CoreError):
    """Raised when a scheme fails the phonemic validation."""


class ParseError(CoreError):
    """Raised when text fails to match the expected phonology or scheme pattern."""


class ConversionError(CoreError):
    """Base exception for errors during conversion operations."""


class NoMatchError(ConversionError):
    """Raised when no matching pattern rule can be resolved for a given sequence or query."""


class ValidationError(CoreError):
    """Base exception for errors during post-conversion operations."""


class PhonologicalError(ValidationError):
    """Raised when a phonological rule violation or invalid feature sequence is encountered."""


class RoundtripError(ValidationError):
    """Raised when result text fails to convert back to its original form inside the solver."""


class CollisionError(ValidationError):
    """Raised when a component collision occurs during round-trip validation."""
