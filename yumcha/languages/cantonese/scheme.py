from typing import Generic

from yumcha.language.scheme import Scheme
from yumcha.language.scheme.representation import (
    IPARepresentationT,
    RepresentationT,
)

from .ipa_representation import CantoneseIPARepresentation


class CantoneseScheme(Scheme, Generic[RepresentationT, IPARepresentationT]):
    @property
    def ipa_representation_class(self) -> type[CantoneseIPARepresentation]:
        return CantoneseIPARepresentation
