from typing import override

from yumcha.language.scheme.pattern_map import PatternDict
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
    def map(self) -> PatternDict:
        return MAP

    @property
    @override
    def one_way_map(self) -> PatternDict:
        return ONE_WAY_MAP
