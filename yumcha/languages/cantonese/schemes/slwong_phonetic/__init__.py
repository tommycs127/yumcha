from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseIPARepresentation, CantoneseScheme

from .representation import SLWongPhoneticRepresentation
from .scheme import MAP


class SLWongPhonetic(
    CantoneseScheme[SLWongPhoneticRepresentation, CantoneseIPARepresentation]
):
    @property
    def representation_class(self) -> type:
        return SLWongPhoneticRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP

    @property
    def name(self) -> str:
        return "SLWong_Phonetic"
