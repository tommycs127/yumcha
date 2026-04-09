from yumcha.language.scheme.feature.types import FeatureDict, InverseFeatureDict
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
    def map(self) -> FeatureDict:
        return MAP

    @property
    def inverse_map(self) -> InverseFeatureDict:
        return INVERSE_MAP

    @property
    def name(self) -> str:
        return "Kuping_Alt"
