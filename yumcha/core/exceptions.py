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


class PhonologicalError(ConversionError):
    """Raised when a phonological rule violation or invalid feature sequence is encountered."""


class NoMatchError(ConversionError):
    """Raised when no matching pattern rule can be resolved for a given sequence or query."""


class NotSupportedError(ConversionError):
    """Raised when validation reveals that the scheme does not support the given sequence."""
