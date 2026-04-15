from typing import override

from yumcha.language.scheme.pattern_map import PatternDict
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
    def map(self) -> PatternDict:
        return MAP

    @property
    @override
    def inverse_map(self) -> PatternDict:
        return INVERSE_MAP
