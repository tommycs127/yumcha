from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import PenkyampRepresentation
from .scheme import INVERSE_MAP, MAP, ONE_WAY_MAP


class Penkyamp(CantoneseScheme[PenkyampRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return PenkyampRepresentation

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
    def inverse_map(self) -> PatternRegistry:
        return INVERSE_MAP
