from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import HangulRepresentation
from .scheme import MAP, ONE_WAY_MAP


class Hangul(CantoneseScheme[HangulRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return HangulRepresentation

    @property
    @override
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        return {
            "initial": ("initial",),
            "nucleus": ("final",),
            "coda": ("final",),
            "tone": ("tone",),
        }

    @property
    @override
    def map(self) -> PatternRegistry:
        return MAP

    @property
    @override
    def one_way_map(self) -> PatternRegistry:
        return ONE_WAY_MAP
