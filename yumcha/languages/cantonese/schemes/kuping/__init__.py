from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import KupingRepresentation
from .scheme import INVERSE_MAP, MAP


class Kuping(CantoneseScheme[KupingRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return KupingRepresentation

    @property
    @override
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        return {
            "initial": ("initial",),
            "nucleus": ("nucleus",),
            "coda": ("coda",),
            "tone": (
                "tone_number",
                "tone",
            ),
        }

    @property
    @override
    def map(self) -> PatternRegistry:
        return MAP

    @property
    @override
    def inverse_map(self) -> PatternRegistry:
        return INVERSE_MAP
