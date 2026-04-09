from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import HangulRepresentation
from .scheme import MAP


class Hangul(CantoneseScheme[HangulRepresentation, CantoneseRepresentation]):
    @property
    def representation_class(self) -> type:
        return HangulRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP
