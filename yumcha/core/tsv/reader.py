import csv
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import IO


def read(
    source: str | Traversable | IO[str],
    encoding: str = "utf-8",
    newline: str = "",
) -> tuple[list[str], list[list[str]]]:
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
