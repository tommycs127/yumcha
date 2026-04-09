from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import YaleRepresentation
from .scheme import MAP


class Yale(CantoneseScheme[YaleRepresentation, CantoneseRepresentation]):
    @property
    def representation_class(self) -> type:
        return YaleRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP
