from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import JyutpingRepresentation
from .scheme import MAP


class Jyutping(CantoneseScheme[JyutpingRepresentation, CantoneseRepresentation]):
    @property
    def representation_class(self) -> type:
        return JyutpingRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP
