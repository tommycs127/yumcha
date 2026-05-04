from dataclasses import dataclass
from typing import override

from yumcha.language import Language
from yumcha.language.schema import Phonology

from .phonology import PHONOLOGY
from .representation import CantoneseRepresentation
from .scheme import CantoneseScheme


@dataclass
class Cantonese(Language[CantoneseScheme, CantoneseRepresentation]):
    @property
    @override
    def phonology(self) -> Phonology:
        return PHONOLOGY

    @property
    @override
    def intermediate_representation_class(self) -> type[CantoneseRepresentation]:
        return CantoneseRepresentation
