"""Advanced multi-process exporter for batched parallel conversion exports."""

from __future__ import annotations

import csv
import os
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from itertools import batched, product
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ..core.facades.phonology import Phonology
    from ..core.iterator.wrappers import ProgressBarWrapper
    from ..core.language import Language
    from ..core.models.representation import PhonologyRepresentation


_worker_language: Language[PhonologyRepresentation] | None = None
_worker_scheme_ids: tuple[str, ...] = ()

type LoaderFnType[PhonologyRepresentationT: PhonologyRepresentation] = Callable[
    ..., Language[PhonologyRepresentationT]
]
type LoaderArgsTypes[PhonologyRepresentationT: PhonologyRepresentation] = (
    tuple[()] | tuple[Phonology[PhonologyRepresentationT]]
)


def _init_worker(
    loader_fn: LoaderFnType[PhonologyRepresentation],
    loader_args: LoaderArgsTypes[PhonologyRepresentation],
    scheme_ids: tuple[str, ...],
) -> None:
    """Initializer for process pool worker tasks."""
    global _worker_language, _worker_scheme_ids
    _worker_language = loader_fn(*loader_args)
    _worker_scheme_ids = scheme_ids


def _export_worker(
    chunk: list[str] | tuple[str, ...],
) -> list[tuple[list[str], list[bool]]]:
    """Worker task executing batch scheme conversion across worker processes."""
    assert _worker_language is not None

    language = _worker_language
    scheme_ids = _worker_scheme_ids
    results: list[tuple[list[str], list[bool]]] = []

    for pattern_tuple_str in chunk:
        row: list[str] = [pattern_tuple_str]
        converted_flags: list[bool] = []

        for scheme_id in scheme_ids:
            converted = language.convert_intermediate_to_scheme(
                pattern_tuple_str, scheme_id, True, False
            )
            if converted:
                row.append(str(converted))
                converted_flags.append(True)
            else:
                row.append("")
                converted_flags.append(False)

        results.append((row, converted_flags))

    return results


def _export_worker_single[PhonologyRepresentationT: PhonologyRepresentation](
    language: Language[PhonologyRepresentationT],
    scheme_ids: tuple[str, ...],
    chunk: list[str] | tuple[str, ...],
) -> list[tuple[list[str], list[bool]]]:
    """Single-threaded chunk converter used when process pooling is disabled."""
    results: list[tuple[list[str], list[bool]]] = []

    for pattern_tuple_str in chunk:
        row: list[str] = [pattern_tuple_str]
        converted_flags: list[bool] = []
        for scheme_id in scheme_ids:
            converted = language.convert_intermediate_to_scheme(
                pattern_tuple_str, scheme_id, True, False
            )
            if converted:
                row.append(str(converted))
                converted_flags.append(True)
            else:
                row.append("")
                converted_flags.append(False)
        results.append((row, converted_flags))

    return results


class Exporter[PhonologyRepresentationT: PhonologyRepresentation]:
    """Exports language conversions concurrently using process pool workers."""

    def __init__(
        self,
        language: Language[PhonologyRepresentationT],
        loader_fn: LoaderFnType[PhonologyRepresentationT] | None = None,
        loader_args: LoaderArgsTypes[PhonologyRepresentationT] = (),
    ):
        """Initializes an Exporter instance with support for multi-process worker creation.

        Args:
            language: The primary `Language` instance.
            loader_fn: Optional factory function to instantiate `Language` in worker processes.
            loader_args: Arguments to pass to `loader_fn` upon worker initialization.
        """
        self.language: Language[PhonologyRepresentationT] = language
        self.loader_fn: LoaderFnType[PhonologyRepresentationT] | None = loader_fn
        self.loader_args: LoaderArgsTypes[PhonologyRepresentationT] = loader_args

    def export(
        self,
        path: str | Path,
        progress_bar: ProgressBarWrapper | None = None,
        max_workers: int | None = None,
        chunk_size: int | None = None,
    ) -> None:
        """Exports generated phonological representations and conversions to a TSV file.

        Args:
            path: Target file path for TSV output.
            progress_bar: Optional progress bar wrapper.
            max_workers: Maximum process workers to use. Defaults to `os.cpu_count()`.
                Note: On resource-constrained devices (e.g., Raspberry Pi) or shared
                servers, set this to `CPU_COUNT - 1` to prevent thermal throttling
                and keep the system responsive.
            chunk_size: Number of representations per worker batch. If `None`,
                dynamically calculated based on total rows and worker count.
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        language = self.language
        schemes = language.schemes
        scheme_ids = tuple(schemes)

        charsets = language.phonology.charsets_sorted
        total_rows = 1
        for c in charsets:
            total_rows *= len(c)

        workers = max_workers or os.cpu_count() or 1

        if chunk_size is None:
            target_chunk = total_rows // (workers * 20)
            chunk_size = max(100, min(5000, target_chunk or 100))

        ir_strings = ("".join(p) for p in product(*charsets))
        chunks = batched(ir_strings, chunk_size)
        total_chunks = (total_rows + chunk_size - 1) // chunk_size

        scheme_counts = [0] * len(scheme_ids)

        with file_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t", lineterminator="\n")
            writer.writerow(["IR", *scheme_ids])

            if self.loader_fn is None:
                chunks_iterable = chunks
                if progress_bar is not None:
                    chunks_iterable = progress_bar(chunks, total=total_chunks)

                for chunk in chunks_iterable:
                    chunk_result = _export_worker_single(language, scheme_ids, chunk)
                    for row, converted_flags in chunk_result:
                        writer.writerow(row)
                        for idx, flag in enumerate(converted_flags):
                            if flag:
                                scheme_counts[idx] += 1
            else:
                loader_fn = cast(
                    "LoaderFnType[PhonologyRepresentation]", self.loader_fn
                )

                with ProcessPoolExecutor(
                    max_workers=workers,
                    initializer=_init_worker,
                    initargs=(loader_fn, self.loader_args, scheme_ids),
                ) as executor:
                    results_generator = executor.map(
                        _export_worker, chunks, chunksize=1
                    )

                    if progress_bar is not None:
                        results_generator = progress_bar(
                            results_generator, total=total_chunks
                        )

                    for chunk_result in results_generator:
                        for row, converted_flags in chunk_result:
                            writer.writerow(row)
                            for idx, flag in enumerate(converted_flags):
                                if flag:
                                    scheme_counts[idx] += 1

            total_counts = [total_rows, *scheme_counts]
            coverages = (
                [f"{rows / total_rows:.2%}" for rows in scheme_counts]
                if total_rows > 0
                else ["0.00%"] * len(scheme_ids)
            )
            writer.writerow(["TOTAL", *coverages])
            writer.writerow(total_counts)
