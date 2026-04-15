from dataclasses import dataclass

from yumcha.language.scheme.representation import Representation, ValidationError


@dataclass(frozen=True)
class KupingRepresentation(Representation):
    REQUIRED = ("nucleus",)
    initial: str
    nucleus: str
    coda: str
    tone_number: str | None  # can be None when self.tone is str
    tone: str | None  # can be None when self.tone_number is str

    def validate(self) -> None:
        invaild_nucleus_coda_comb = {
            "i": "i",
            "y": "y",
            "u": "u",
            "m": "m",
            "ŋ": "ŋ",
        }

        if (
            self.nucleus in invaild_nucleus_coda_comb
            and self.coda == invaild_nucleus_coda_comb[self.nucleus]
        ):
            raise ValidationError(
                f"nucleus '{self.nucleus}' cannot be with coda '{self.coda}'"
            )

        def _wrong_tone(suggestions: tuple[str, ...]):
            final = self.initial + self.nucleus + self.coda
            suggestions_str = (
                suggestions[-1]
                if len(suggestions) == 1
                else ", ".join(suggestions[:-1]) + f" or {suggestions[-1]}"
            )
            raise ValidationError(
                f"final '{final}' cannot be with tone '{self.tone}'. "
                f"Did you mean {suggestions_str} for tone?"
            )

        if self.tone_number is None and self.tone is None:
            raise ValidationError(
                "KupingRepresentation missing 1 required keyword argument: "
                "'tone_number' or 'tone'"
            )

        checked_coda = ("p", "t", "k")
        checked_tone_number = ("", "55", "33", "22")
        checked_tone = ("^4", "-4", "_4")

        if (
            self.coda in checked_coda
            and self.tone_number
            and self.tone_number not in checked_tone_number
        ):
            raise ValidationError(
                f"tone number of '{str(self)}' does not have corresponding tone. "
                "Tone sandhi of syllable with checked coda is not supported"
            )

        if self.coda in checked_coda and self.tone and self.tone not in checked_tone:
            register = self.tone[0]
            _wrong_tone((f"'{register}4'",))

        if (
            self.coda not in checked_coda
            and self.tone is not None
            and self.tone in checked_tone
        ):
            register = self.tone[0]
            non_checked_tone_name = ("1", "2", "3")
            registers = tuple(f"'{register}{name}'" for name in non_checked_tone_name)
            _wrong_tone(registers)
