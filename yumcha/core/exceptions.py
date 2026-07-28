from importlib.resources.abc import Traversable


class FileError(Exception):
    """Base class for errors raised during file processing operations.

    Attributes:
        verb (str): The operational action verb used when formatting exception messages.
        path (str | Traversable): The file path or traversable resource object where the error occurred.
        cause (Exception | None): The underlying exception that triggered this error, if available.
    """

    verb: str = "process"

    def __init__(
        self,
        path: str | Traversable,
        cause: Exception | None = None,
    ) -> None:
        """Initializes a FileError with the affected path and optional root cause.

        Args:
            path: The file path or traversable resource where the failure occurred.
            cause: An optional exception instance representing the root cause of the error.
        """
        self.path = path
        self.cause = cause

        filename = path.name if isinstance(path, Traversable) else str(path)
        message = f"failed to {self.verb} file {filename!r}"
        if cause:
            message += f": {cause}"

        super().__init__(message)


class ReadError(FileError, OSError):
    """Raised when an I/O reading operation fails on a file or resource."""

    verb = "read"


class ParseError(FileError, ValueError):
    """Raised when parsing contents from a file fails due to structural or syntax invalidity."""

    verb = "parse"


class PhonologicalError(ValueError):
    """Raised when a phonological rule violation or invalid feature sequence is encountered."""


class AmbiguousMatchError(ValueError):
    """Raised when multiple conflicting patterns match a single input sequence identically."""


class NoMatchError(ValueError):
    """Raised when no matching pattern rule can be resolved for a given sequence or query."""


class ConflictingMatchError(ValueError):
    """Raised when bidirectional validation discovers an inconsistent reverse mapping.

    Occurs during transformation validation when mapping A -> B expects a symmetric reverse mapping B -> A,
    but instead resolves to an conflicting target (e.g., B <-> C).
    """
