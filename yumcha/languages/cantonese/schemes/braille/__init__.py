from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseIPARepresentation, CantoneseScheme

from .representation import BrailleRepresentation
from .scheme import MAP


class Braille(CantoneseScheme[BrailleRepresentation, CantoneseIPARepresentation]):
    @property
    def representation_class(self) -> type:
        return BrailleRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP
