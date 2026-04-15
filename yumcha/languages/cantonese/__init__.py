from dataclasses import dataclass
from typing import override

from yumcha.language import Language
from yumcha.language.scheme.pattern_map import PatternTuple

from .phonology import PHONOLOGY
from .representation import CantoneseRepresentation
from .scheme import CantoneseScheme


@dataclass
class Cantonese(Language[CantoneseScheme, CantoneseRepresentation]):
    @property
    @override
    def phonology(self) -> tuple[PatternTuple, ...]:
        return PHONOLOGY

    @property
    @override
    def intermediate_representation_class(self) -> type[CantoneseRepresentation]:
        return CantoneseRepresentation
