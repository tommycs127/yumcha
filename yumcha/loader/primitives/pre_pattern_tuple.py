"""Type definitions for intermediate pattern tuple representations used during parsing.

Attributes:
    PrePatternTuple: A tuple of `Pattern` elements representing raw unvalidated pattern tuple values.
"""

from ...core.primitives.pattern import Pattern

type PrePatternTuple = tuple[Pattern, ...]
