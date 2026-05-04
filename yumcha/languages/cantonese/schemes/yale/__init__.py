from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import YaleRepresentation
from .scheme import MAP, ONE_WAY_MAP


class Yale(CantoneseScheme[YaleRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return YaleRepresentation

    @property
    @override
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        return {
            "initial": ("initial",),
            "nucleus": (
                "nucleus_before_tone_diacritic",
                "nucleus_after_tone_diacritic",
            ),
            "coda": (
                "coda_vowel",
                "coda_consonant",
            ),
            "tone": (
                "tone_diacritic",
                "tone_h",
            ),
        }

    @property
    @override
    def map(self) -> PatternRegistry:
        return MAP

    @property
    @override
    def one_way_map(self) -> PatternRegistry:
        return ONE_WAY_MAP
