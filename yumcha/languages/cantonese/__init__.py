from dataclasses import dataclass

from yumcha.language import Language
from yumcha.language.scheme.feature.types import FeatureTuple

from .ipa_representation import CantoneseIPARepresentation
from .phonology import PHONOLOGY
from .scheme import CantoneseScheme


@dataclass
class Cantonese(Language[CantoneseScheme, CantoneseIPARepresentation]):
    @property
    def phonology(self) -> tuple[FeatureTuple, ...]:
        return PHONOLOGY

    @property
    def ipa_representation_class(self) -> type[CantoneseIPARepresentation]:
        return CantoneseIPARepresentation
