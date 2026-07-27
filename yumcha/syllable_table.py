from __future__ import annotations

import inspect
import math
from collections.abc import Iterable, Iterator
from itertools import product
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

from .core.pattern_tuple import PatternTuple

if TYPE_CHECKING:
    from .language import Language


T = TypeVar("T")


class ProgressBarWrapper(Protocol):
    def __call__(
        self,
        iterable: Iterable[T],
        *,
        total: int | None = None,
        **kwargs: Any,
    ) -> Iterable[T]: ...


class SyllableTable:
    lang: Language
    scheme_item_counts: list[int]
    progress_bar: ProgressBarWrapper | None

    def __init__(
        self,
        lang: Language,
        progress_bar: ProgressBarWrapper | None = None,
    ):
        self.lang = lang
        self.progress_bar = progress_bar

        scheme_ids = tuple(self.lang.schemes)
        self._scheme_ids = scheme_ids
        self.scheme_item_counts = [0] * len(scheme_ids)

    def __iter__(self) -> Iterator[list[str]]:
        scheme_ids = tuple(self.lang.schemes)
        self.scheme_item_counts = [0] * len(scheme_ids)

        pron_tuples = product(*self.lang.phonology.charsets_sorted)
        progress_bar = self.progress_bar

        if progress_bar is not None:
            signature = inspect.signature(progress_bar)
            if "total" in signature.parameters or any(
                p.kind == p.VAR_KEYWORD for p in signature.parameters.values()
            ):
                pron_tuples = progress_bar(pron_tuples, total=self.total_rows)
            else:
                pron_tuples = progress_bar(pron_tuples)

        for pron_tuple in pron_tuples:
            pattern_tuple = PatternTuple(pron_tuple)
            row = [pattern_tuple.to_string()]

            for idx, scheme_id in enumerate(scheme_ids):
                item = self.lang.to_scheme(scheme_id, pattern_tuple, True, False)
                if item:
                    row.append(str(item))
                    self.scheme_item_counts[idx] += 1
                else:
                    row.append("")

            yield row

    @property
    def scheme_ids(self) -> tuple[str, ...]:
        return tuple(self.lang.schemes)

    @property
    def headers(self):
        return ["IR", *self.lang.schemes]

    @property
    def footers(self):
        return [self.total_rows, *self.scheme_item_counts]

    @property
    def total_rows(self) -> int:
        return math.prod(len(c) for c in self.lang.phonology.charsets_sorted)
