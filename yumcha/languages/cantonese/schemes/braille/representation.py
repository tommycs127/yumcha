from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation


@dataclass(frozen=True)
class BrailleRepresentation(Representation):
    REQUIRED = ("rime", "tone")
    initial: str
    rime: str
    tone: str

    def validate(self) -> None: ...
