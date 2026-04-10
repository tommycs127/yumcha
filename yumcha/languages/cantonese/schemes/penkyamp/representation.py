from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation


@dataclass(frozen=True)
class PenkyampRepresentation(Representation):
    REQUIRED = ("nucleus", "tone")
    initial: str
    nucleus: str
    tone: str
    coda: str

    def validate(self) -> None: ...
