from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class MeyerWempeRepresentation(Representation):
    REQUIRED = ("nucleus", "tone")
    initial: str
    nucleus: str
    coda_vowel: str
    tone: str
    coda_consonant: str

    def validate(self) -> None:
        invaild_nucleus_coda_comb = {
            "i": "i",
            "y": "y",
            "u": "u",
            "m": "m",
            "ng": "ng",
        }

        coda = self.coda_vowel + self.coda_consonant

        if (
            self.nucleus in invaild_nucleus_coda_comb
            and coda == invaild_nucleus_coda_comb[self.nucleus]
        ):
            raise ValidationError(
                f"nucleus '{self.nucleus}' cannot be with coda '{coda}'"
            )
