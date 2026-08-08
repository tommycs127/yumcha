"""Basic single-threaded sequential exporter for phonological representations."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from ..core.iterator import LanguageIterator

if TYPE_CHECKING:
    from ..core.iterator.wrappers import ProgressBarWrapper
    from ..core.language import Language
    from ..core.models.representation import PhonologyRepresentation


class BasicExporter[PhonologyRepresentationT: PhonologyRepresentation]:
    """Handles basic, single-threaded export of language representations to TSV."""

    def __init__(self, language: Language[PhonologyRepresentationT]):
        """Initializes a BasicExporter instance.

        Args:
            language: The `Language` instance to export data from.
        """
        self.language = language

    def export(
        self,
        path: str | Path,
        progress_bar: ProgressBarWrapper | None = None,
    ) -> None:
        """Exports all generated phonological representations and scheme conversions to a TSV file.

        Args:
            path: Target file path for the TSV output.
            progress_bar: Optional progress bar wrapper instance.
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        iterator = LanguageIterator(self.language, progress_bar=progress_bar)

        with file_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(iterator.headers)
            writer.writerows(iterator)
            total_counts = iterator.current_counts
            total_rows = iterator.total_rows
            coverages = (
                [f"{rows / total_rows:.2%}" for rows in total_counts[1:]]
                if total_rows > 0
                else ["0.00%"] * len(iterator.scheme_ids)
            )
            writer.writerow(["TOTAL", *coverages])
            writer.writerow(total_counts)
