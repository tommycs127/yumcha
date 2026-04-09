from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import RaoRepresentation
from .scheme import MAP


class Rao(CantoneseScheme[RaoRepresentation, CantoneseRepresentation]):
    @property
    def representation_class(self) -> type:
        return RaoRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP
