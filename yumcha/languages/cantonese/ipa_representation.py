from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class CantoneseIPARepresentation(Representation):
    REQUIRED = ("nucleus", "tone")
    initial: str
    nucleus: str
    coda: str
    tone: str

    def validate(self) -> None:
        invalid_initial_nucleus_comb = {
            "m": "m̩",
            "ŋ": "ŋ̩",
        }

        if (
            self.initial in invalid_initial_nucleus_comb
            and self.nucleus == invalid_initial_nucleus_comb[self.initial]
        ):
            raise ValidationError(
                f"initial '{self.initial}' cannot be with nucleus '{self.nucleus}'"
            )

        invaild_nucleus_coda_comb = {
            "iː": "i̯",
            "uː": "u̯",
            "yː": "y̯",
            "m̩": "m",
            "ŋ̩": "ŋ",
        }

        if (
            self.nucleus in invaild_nucleus_coda_comb
            and self.coda == invaild_nucleus_coda_comb[self.nucleus]
        ):
            raise ValidationError(
                f"nucleus '{self.nucleus}' cannot be with coda '{self.coda}'"
            )

        syllabic_consonants = ("m̩", "ŋ̩")

        if self.nucleus in syllabic_consonants and self.coda:
            raise ValidationError(
                f"syllabic consonant nucleus '{self.nucleus}' "
                f"cannot be with coda '{self.coda}'"
            )
