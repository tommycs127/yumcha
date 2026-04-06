from yumcha.language.scheme.feature.types import FeatureDict, InverseFeatureDict
from yumcha.languages.cantonese import CantoneseIPARepresentation, CantoneseScheme

from .representation import SidneyLauRepresentation
from .scheme import INVERSE_MAP, MAP


class SidneyLau(CantoneseScheme[SidneyLauRepresentation, CantoneseIPARepresentation]):
    @property
    def representation_class(self) -> type:
        return SidneyLauRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP

    @property
    def inverse_map(self) -> InverseFeatureDict:
        return INVERSE_MAP
