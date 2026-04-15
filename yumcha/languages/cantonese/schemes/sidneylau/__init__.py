from typing import override

from yumcha.language.scheme.pattern_map import PatternDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import SidneyLauRepresentation
from .scheme import INVERSE_MAP, MAP, ONE_WAY_MAP


class SidneyLau(CantoneseScheme[SidneyLauRepresentation, CantoneseRepresentation]):
    @property
    @override
    def representation_class(self) -> type:
        return SidneyLauRepresentation

    @property
    @override
    def map(self) -> PatternDict:
        return MAP

    @property
    @override
    def one_way_map(self) -> PatternDict:
        return ONE_WAY_MAP

    @property
    @override
    def inverse_map(self) -> PatternDict:
        return INVERSE_MAP
