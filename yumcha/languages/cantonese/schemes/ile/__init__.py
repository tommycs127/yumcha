from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseIPARepresentation, CantoneseScheme

from .representation import ILERepresentation
from .scheme import MAP


class ILE(CantoneseScheme[ILERepresentation, CantoneseIPARepresentation]):
    @property
    def representation_class(self) -> type:
        return ILERepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP
