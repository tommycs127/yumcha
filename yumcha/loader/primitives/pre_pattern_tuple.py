"""Type definitions for intermediate pattern tuple representations used during parsing."""

from ...core.primitives.pattern import Pattern

type PrePatternTuple = tuple[Pattern, ...]
"""Type alias representing a tuple of `Pattern` elements representing raw unvalidated pattern tuple values."""
