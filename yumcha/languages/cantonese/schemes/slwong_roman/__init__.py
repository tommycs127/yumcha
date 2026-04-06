from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseIPARepresentation, CantoneseScheme

from .representation import SLWongRomanRepresentation
from .scheme import MAP


class SLWongRoman(
    CantoneseScheme[SLWongRomanRepresentation, CantoneseIPARepresentation]
):
    @property
    def representation_class(self) -> type:
        return SLWongRomanRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP

    @property
    def name(self) -> str:
        return "SLWong_Roman"
