from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class YaleRepresentation(Representation):
    REQUIRED = (
        "nucleus_before_tone_diacritic",
        "nucleus_after_tone_diacritic",
        "tone_diacritic",
        "tone_h",
    )
    initial: str
    nucleus_before_tone_diacritic: str
    tone_diacritic: str
    nucleus_after_tone_diacritic: str
    coda_vowel: str
    tone_h: str
    coda_consonant: str

    def validate(self) -> None:
        nucleus = self.nucleus_before_tone_diacritic + self.nucleus_after_tone_diacritic
        coda = self.coda_vowel or self.coda_consonant

        invaild_nucleus_coda_comb = {
            "i": "i",
            "u": "u",
            "m": "m",
            "ng": "ng",
        }

        if (
            nucleus in invaild_nucleus_coda_comb
            and coda == invaild_nucleus_coda_comb[nucleus]
        ):
            raise ValidationError(f"nucleus '{nucleus}' cannot be with coda '{coda}'")
