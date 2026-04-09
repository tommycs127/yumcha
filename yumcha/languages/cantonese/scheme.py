from typing import Generic

from yumcha.language.scheme import Scheme
from yumcha.language.scheme.representation import (
    IntermediateRepresentationT,
    RepresentationT,
)

from .representation import CantoneseRepresentation


class CantoneseScheme(Scheme, Generic[RepresentationT, IntermediateRepresentationT]):
    @property
    def intermediate_representation_class(self) -> type[CantoneseRepresentation]:
        return CantoneseRepresentation
