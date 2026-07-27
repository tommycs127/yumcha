import csv
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from .core.exceptions import ParseError, ReadError
from .core.models import Representation
from .core.tsv.loader import load_phonology
from .language import Language
from .syllable_table import ProgressBarWrapper


def load_language(
    language: str,
    directory: str | Traversable | None = None,
    phonology_file_name: str = "phonology.tsv",
    schemes_folder_name: str = "schemes",
) -> Language[Representation, Representation]:
    if directory is None:
        directory = resources.files("yumcha") / "languages"
    elif isinstance(directory, str):
        directory = Path(directory)

    lang_dir = directory / language

    phonology_resource = lang_dir / phonology_file_name

    try:
        phonology = load_phonology(phonology_resource)
    except OSError as e:
        raise ReadError(phonology_file_name, cause=e) from e
    except ValueError as e:
        raise ParseError(phonology_file_name, cause=e) from e

    lang = Language(phonology)

    schemes_dir = lang_dir / schemes_folder_name

    if schemes_dir.is_dir():
        for scheme_resource in schemes_dir.iterdir():
            if not scheme_resource.is_file():
                continue

            lang.add_scheme(scheme_resource)

    return lang


def write_syllable_table(
    language: Language[Representation, Representation],
    output_path: str | Path,
    progress_bar: ProgressBarWrapper | None = None,
):
    path = Path(output_path)
    if path.suffix.lower() != ".tsv":
        path = path.with_suffix(".tsv")

    path.parent.mkdir(parents=True, exist_ok=True)

    table = language.syllable_table(progress_bar)

    with open(path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(table.headers)

        for row in table:
            writer.writerow(row)

        footers = table.footers
        total_rows = table.total_rows
        coverages = [f"{rows / total_rows:.2%}" for rows in footers[1:]]

        writer.writerow(["TOTAL", *coverages])
        writer.writerow(footers)
