"""Low-level file and stream reader utilities for TSV format input."""

import csv
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import IO


def read(
    source: str | Traversable | IO[str],
    encoding: str = "utf-8",
    newline: str = "",
) -> tuple[list[str], list[list[str]]]:
    """Reads and parses a TSV (tab-separated values) file or stream into headers and data rows.

    Supports reading from file paths (string or `Path`), `Traversable` resource objects,
    or open text streams (`IO[str]`).

    Args:
        source: File path, `Traversable` resource, or open readable text stream.
        encoding: Text encoding to use when opening file paths or traversables. Defaults to "utf-8".
        newline: Newline processing control when opening files. Defaults to "".

    Returns:
        A tuple containing:
            - `headers`: A list of strings representing the header row.
            - `data`: A list of rows, where each row is a list of cell string values.

    Raises:
        ValueError: If the file or stream contains no non-empty rows.
    """

    def _parse_stream(stream: IO[str]) -> tuple[list[str], list[list[str]]]:
        tsv_reader = csv.reader(stream, delimiter="\t")
        clean_rows = [row for row in tsv_reader if row]

        if not clean_rows:
            raise ValueError("empty file")

        return clean_rows[0], clean_rows[1:]

    if isinstance(source, (str, Path)):
        with open(source, mode="r", encoding=encoding, newline=newline) as file:
            return _parse_stream(file)

    if isinstance(source, Traversable):
        with source.open(mode="r", encoding=encoding) as file:
            return _parse_stream(file)

    return _parse_stream(source)
