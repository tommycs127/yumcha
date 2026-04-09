from yumcha.language.scheme.feature.types import FeatureDict, InverseFeatureDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import KupingRepresentation
from .scheme import INVERSE_MAP, MAP


class Kuping(CantoneseScheme[KupingRepresentation, CantoneseRepresentation]):
    @property
    def representation_class(self) -> type:
        return KupingRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP

    @property
    def inverse_map(self) -> InverseFeatureDict:
        return INVERSE_MAP
