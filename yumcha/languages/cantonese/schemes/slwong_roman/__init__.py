from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import SLWongRomanRepresentation
from .scheme import MAP, ONE_WAY_MAP


class SLWongRoman(CantoneseScheme[SLWongRomanRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return SLWongRomanRepresentation

    @property
    @override
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        return {
            "initial": ("initial",),
            "nucleus": ("nucleus",),
            "coda": ("coda",),
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

    @property
    @override
    def code(self) -> str:
        return "slwong_roman"
