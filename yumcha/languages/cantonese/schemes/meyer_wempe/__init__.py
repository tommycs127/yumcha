from typing import override

from yumcha.language.scheme.schema import PatternRegistry
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import MeyerWempeRepresentation
from .scheme import MAP, ONE_WAY_MAP


class MeyerWempe(CantoneseScheme[MeyerWempeRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return MeyerWempeRepresentation

    @property
    @override
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        return {
            "initial": ("initial",),
            "nucleus": ("nucleus",),
            "coda": (
                "coda_vowel",
                "coda_consonant",
            ),
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
        return "meyer_wempe"
