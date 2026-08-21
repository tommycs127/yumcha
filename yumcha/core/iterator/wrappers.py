"""Wrapper protocol definitions for external iteration utilities."""

from collections.abc import Callable, Iterable
from typing import Never

type ProgressBarWrapper = Callable[..., Iterable[Never]]
"""Protocol signature for progress bar wrapper callables (e.g., `tqdm`)."""
