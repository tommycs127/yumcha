from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class HangulRepresentation(Representation):
    REQUIRED = ("final", "tone")
    initial: str
    final: str
    tone: str

    def validate(self) -> None: ...
