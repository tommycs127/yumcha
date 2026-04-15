from typing import override

from yumcha.language.scheme import Scheme
from yumcha.language.scheme.representation import Representation

from .representation import CantoneseRepresentation


class CantoneseScheme[RT: Representation, IRT: Representation](Scheme):
    @property
    @override
    def intermediate_representation_class(self) -> type[CantoneseRepresentation]:
        return CantoneseRepresentation
