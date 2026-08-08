"""Utility functions for processing text and cell data during resource parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.primitives.pattern import Pattern


def parse_data_cell(s: str) -> Pattern:
    """Parses a single TSV data cell into a pattern value or Ellipsis wildcard.

    Args:
        s: Raw string contents of a table cell.

    Returns:
        The string cell content, or `Ellipsis` (`...`) if the cell represents a wildcard.
    """
    stripped = s.strip()
    return ... if stripped == "..." else stripped
