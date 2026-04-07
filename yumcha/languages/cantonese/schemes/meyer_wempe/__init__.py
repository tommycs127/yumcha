from yumcha.language.scheme.feature.types import FeatureDict
from yumcha.languages.cantonese import CantoneseIPARepresentation, CantoneseScheme

from .representation import MeyerWempeRepresentation
from .scheme import MAP


class MeyerWempe(CantoneseScheme[MeyerWempeRepresentation, CantoneseIPARepresentation]):
    @property
    def representation_class(self) -> type:
        return MeyerWempeRepresentation

    @property
    def map(self) -> FeatureDict:
        return MAP

    @property
    def name(self) -> str:
        return "Meyer_Wempe"
