from dataclasses import dataclass

from yumcha.language import Language
from yumcha.language.scheme.feature.types import FeatureTuple

from .phonology import PHONOLOGY
from .representation import CantoneseRepresentation
from .scheme import CantoneseScheme


@dataclass
class Cantonese(Language[CantoneseScheme, CantoneseRepresentation]):
    @property
    def phonology(self) -> tuple[FeatureTuple, ...]:
        return PHONOLOGY

    @property
    def intermediate_representation_class(self) -> type[CantoneseRepresentation]:
        return CantoneseRepresentation
