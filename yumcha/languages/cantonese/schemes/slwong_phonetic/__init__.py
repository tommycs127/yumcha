from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseRepresentation, CantoneseScheme

from .representation import SLWongPhoneticRepresentation
from .scheme import MAP


class SLWongPhonetic(
    CantoneseScheme[SLWongPhoneticRepresentation, CantoneseRepresentation]
):
    @property
    def representation_class(self) -> type:
        return SLWongPhoneticRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP

    @property
    def code(self) -> str:
        return "slwong_phonetic"
