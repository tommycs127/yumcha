from importlib.resources.abc import Traversable


class FileError(Exception):
    """Base class for errors during file operations."""

    verb: str = "process"

    def __init__(
        self,
        path: str | Traversable,
        cause: Exception | None = None,
    ) -> None:
        self.path = path
        self.cause = cause

        filename = path.name if isinstance(path, Traversable) else str(path)
        message = f"failed to {self.verb} file {filename!r}"
        if cause:
            message += f": {cause}"

        super().__init__(message)


class ReadError(FileError, OSError):
    verb = "read"


class ParseError(FileError, ValueError):
    verb = "parse"


class PhonologicalError(ValueError):
    pass


class AmbiguousMatchError(ValueError):
    pass


class NoMatchError(ValueError):
    pass


class ConflictingMatchError(ValueError):
    pass
