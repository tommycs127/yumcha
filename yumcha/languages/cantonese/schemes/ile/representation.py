from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class ILERepresentation(Representation):
    REQUIRED = ("nucleus", "tone")
    initial: str
    nucleus: str
    coda: str
    tone: str

    def validate(self) -> None:
        invaild_nucleus_coda_comb = {
            "i": "i",
            "y": "y",
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

        def _wrong_tone(suggested_tone_tuple: tuple[str, ...], idx: int) -> None:
            suggested_tone = suggested_tone_tuple[idx]
            raise ValidationError(
                f"checked coda '{self.coda}' cannot be with tone '{self.tone}'. "
                f"Did you mean tone '{suggested_tone}'?"
            )

        checked_coda = ("p", "t", "k")
        non_checked_tone = ("1", "3", "6")
        checked_tone = ("7", "8", "9")

        if self.coda in checked_coda and self.tone in non_checked_tone:
            _wrong_tone(checked_tone, non_checked_tone.index(self.tone))

        if self.coda not in checked_coda and self.tone in checked_tone:
            _wrong_tone(non_checked_tone, checked_tone.index(self.tone))
