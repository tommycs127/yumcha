from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class SidneyLauRepresentation(Representation):
    REQUIRED = ("nucleus", "tone")
    initial: str
    nucleus: str
    coda: str
    tone: str

    def validate(self) -> None:
        invaild_nucleus_coda_comb = {
            "i": "i",
            "u": "u",
            "m": "m",
            "ng": "ng",
        }

        if (
            self.nucleus in invaild_nucleus_coda_comb
            and self.coda == invaild_nucleus_coda_comb[self.nucleus]
        ):
            raise ValidationError(
                f"nucleus '{self.nucleus}' cannot be with coda '{self.coda}'"
            )

        if self.nucleus == "e" and self.coda == "u":
            raise ValidationError(
                f"invalid syllable: nucleus '{self.nucleus}' and coda '{self.coda}'"
            )
