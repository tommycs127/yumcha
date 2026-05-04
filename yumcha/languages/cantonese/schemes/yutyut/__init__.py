from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import YutyutRepresentation
from .scheme import MAP, ONE_WAY_MAP


class Yutyut(CantoneseScheme[YutyutRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return YutyutRepresentation

    @property
    @override
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        return {
            "initial": ("initial",),
            "nucleus": (
                "nucleus_before_tone",
                "nucleus_after_tone",
            ),
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
