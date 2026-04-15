from yumcha.language.scheme.pattern_map import PatternDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import KupingAlternativeRepresentation
from .scheme import INVERSE_MAP, MAP


class KupingAlternative(
    CantoneseScheme[KupingAlternativeRepresentation, CantoneseRepresentation]
):
    @property
    def representation_class(self) -> type:
        return KupingAlternativeRepresentation

    @property
    def map(self) -> PatternDict:
        return MAP

    @property
    def inverse_map(self) -> PatternDict:
        return INVERSE_MAP

    @property
    def code(self) -> str:
        return "kuping_alt"
