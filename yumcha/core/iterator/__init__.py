"""Language iterator for cross-scheme conversion and table generation."""

from __future__ import annotations

import inspect
import math
from collections.abc import Iterator, Sequence
from itertools import product
from typing import TYPE_CHECKING

from ..utils.collections import SequenceProxy

if TYPE_CHECKING:
    from ..language import Language
    from ..models.representation import PhonologyRepresentation
    from .wrappers import ProgressBarWrapper


class LanguageIterator[PhonologyRepresentationT: PhonologyRepresentation]:
    """Iterates over Cartesian phonology combinations and converts across schemes.

    Attributes:
        language: Active `Language` facade containing phonology and scheme models.
        progress_bar: Optional progress bar wrapper callable applied during iteration.
    """

    def __init__(
        self,
        language: Language[PhonologyRepresentationT],
        progress_bar: ProgressBarWrapper | None = None,
    ) -> None:
        """Initializes the language iterator.

        Args:
            language: Language facade instance to iterate over.
            progress_bar: Optional wrapper function for reporting iteration progress.
        """
        self.language = language
        self._scheme_item_counts = [0] * len(language.schemes)
        self._scheme_item_counts_view = SequenceProxy(self._scheme_item_counts)

        self.progress_bar = progress_bar
        self._progress_bar_supports_arg_total = False
        if progress_bar is not None:
            sig = inspect.signature(progress_bar)
            self._progress_bar_supports_arg_total = "total" in sig.parameters or any(
                p.kind == p.VAR_KEYWORD for p in sig.parameters.values()
            )

    def __iter__(self) -> Iterator[Sequence[str]]:
        """Yields table rows mapping intermediate phonology to scheme conversions.

        Yields:
            A list representing a table row where the first element is the intermediate
            phonological string, followed by converted strings for each registered scheme
            (or empty strings for unconvertible combinations).
        """
        schemes = self.language.schemes
        scheme_ids = tuple(schemes)
        self._scheme_item_counts[:] = [0] * len(schemes)

        intermediate_pattern_tuples = product(*self.language.phonology.charsets_sorted)

        progress_bar = self.progress_bar
        if progress_bar is not None:
            if self._progress_bar_supports_arg_total:
                intermediate_pattern_tuples = progress_bar(
                    intermediate_pattern_tuples,
                    total=self.total_rows,
                )
            else:
                intermediate_pattern_tuples = progress_bar(intermediate_pattern_tuples)

        convert_intermediate_to_scheme = self.language.convert_intermediate_to_scheme
        _scheme_item_counts = self._scheme_item_counts

        for intermediate_pattern_tuple in intermediate_pattern_tuples:
            pattern_tuple_str = "".join(intermediate_pattern_tuple)
            row = [pattern_tuple_str]

            for idx, scheme_id in enumerate(scheme_ids):
                converted = convert_intermediate_to_scheme(
                    pattern_tuple_str, scheme_id, True, False
                )
                if converted:
                    row.append(str(converted))
                    _scheme_item_counts[idx] += 1
                else:
                    row.append("")

            yield row

    @property
    def scheme_item_counts(self) -> SequenceProxy[int]:
        """Gets a read-only view of valid conversion counts per scheme.

        Returns:
            A read-only sequence proxy containing item count totals for each scheme.
        """
        return self._scheme_item_counts_view

    @property
    def scheme_ids(self) -> tuple[str, ...]:
        """Gets the registered scheme identifiers for the active language.

        Returns:
            A tuple of scheme ID strings.
        """
        return tuple(self.language.schemes)

    @property
    def headers(self) -> list[str]:
        """Gets table column headers.

        Returns:
            A list of column names, starting with "IR" followed by scheme IDs.
        """
        return ["IR", *self.language.schemes]

    @property
    def current_counts(self) -> list[int]:
        """Gets current total row and scheme conversion counts.

        Returns:
            A list starting with total row count followed by conversion counts per scheme.
        """
        return [self.total_rows, *self.scheme_item_counts]

    @property
    def total_rows(self) -> int:
        """Calculates the total possible combination count (Cartesian product length).

        Returns:
            Total row count as an integer.
        """
        return math.prod(len(c) for c in self.language.phonology.charsets_sorted)
