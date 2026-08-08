"""Wrapper protocol definitions for external iteration utilities."""

from collections.abc import Iterable
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class ProgressBarWrapper(Protocol):
    """Protocol signature for progress bar wrapper callables (e.g., `tqdm`)."""

    def __call__(
        self,
        iterable: Iterable[T],
        *,
        total: int | None = None,
        **kwargs: Any,
    ) -> Iterable[T]: ...
