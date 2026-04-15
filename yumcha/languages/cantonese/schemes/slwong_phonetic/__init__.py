from typing import override

from yumcha.language.scheme.pattern_map import PatternDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import SLWongPhoneticRepresentation
from .scheme import MAP, ONE_WAY_MAP


class SLWongPhonetic(
    CantoneseScheme[SLWongPhoneticRepresentation, CantoneseRepresentation]
):
    @property
    @override
    def representation_class(self) -> type:
        return SLWongPhoneticRepresentation

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
    def code(self) -> str:
        return "slwong_phonetic"
