"""Pattern type definitions.

Defines core type aliases for pattern elements, representing either concrete
string elements or wildcard placeholders.
"""

from types import EllipsisType

type Pattern = str | EllipsisType
"""Type alias representing either a character pattern string or an wildcard (`...`)."""
