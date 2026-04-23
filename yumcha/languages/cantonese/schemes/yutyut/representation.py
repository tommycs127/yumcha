from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation


@dataclass(frozen=True)
class YutyutRepresentation(Representation):
    REQUIRED = ("nucleus_before_tone", "tone", "nucleus_after_tone")
    initial: str
    nucleus_before_tone: str
    tone: str
    nucleus_after_tone: str
    coda: str

    def validate(self) -> None: ...
