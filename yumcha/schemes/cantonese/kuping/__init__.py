from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseReading,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneName,
    CantoneseVowel,
)
from yumcha.schemes.cantonese import CantoneseScheme, ParsedCantoneseScheme
from yumcha.schemes.cantonese.kuping.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.kuping.regex import REGEX_PATTERN
from yumcha.schemes.typing import SchemeMap


class ParsedKuping(ParsedCantoneseScheme):
    pass


class Kuping(CantoneseScheme):
    name = "Kuping"

    TONE_FROM_LETTER = {
        "unchecked": {
            "55": "^1",
            "53": "^1",
            "35": "^2",
            "33": "^3",
            "11": "_1",
            "21": "_1",
            "13": "_2",
            "22": "_3",
        },
        "checked": {
            "55": "^4",
            "33": "-4",
            "22": "_4",
        },
    }

    @property
    def PARSED_CLASS(self) -> type[ParsedKuping]:
        return ParsedKuping

    @property
    def MAP(self) -> SchemeMap:
        return {
            "initial_to_object": INITIAL_TO_OBJECT,
            "object_to_initial": OBJECT_TO_INITIAL,
            "medial_to_object": dict(),
            "object_to_medial": dict(),
            "nucleus_to_object": NUCLEUS_TO_OBJECT,
            "object_to_nucleus": OBJECT_TO_NUCLEUS,
            "coda_to_object": CODA_TO_OBJECT,
            "object_to_coda": OBJECT_TO_CODA,
            "tone_to_object": TONE_TO_OBJECT,
            "object_to_tone": OBJECT_TO_TONE,
        }

    def get_unnormalized_parsed(self, text: str) -> ParsedKuping:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        g = m.groups()
        initial = g[0]
        nucleus = g[1]
        coda = g[2]
        tone_letters = g[4] or ""
        tone_category = g[5] or g[6] or ""

        return ParsedKuping(
            initial=initial if initial else None,
            medial=None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=f"{tone_letters};{tone_category}",
        )

    def normalize_input(self, parsed: ParsedKuping) -> ParsedKuping:
        if not isinstance(parsed.tone, str):
            raise ValueError("Tone is not str")
        tone_letters, tone_category = parsed.tone.split(";")

        if not tone_category:
            coda_category = (
                "checked"
                if parsed.coda and parsed.coda[-1] in ["p", "t", "k"]
                else "unchecked"
            )
            tone_category = self.TONE_FROM_LETTER[coda_category].get(tone_letters, None)
            if tone_category is None:
                raise ValueError(
                    f"Invalid {self.name} syllable: {self.compose(parsed)}"
                )

        return ParsedKuping(
            initial=parsed.initial,
            medial=None,
            nucleus=parsed.nucleus,
            coda=parsed.coda,
            tone=f"{tone_letters};{tone_category}",
        )

    def get_unprocessed_tone(self, parsed: ParsedKuping) -> CantoneseTone:
        if not isinstance(parsed.tone, str):
            raise ValueError("Tone is not str")
        tone_letters, tone_category = parsed.tone[:-2], parsed.tone[-2:]
        return self.MAP["tone_to_object"][tone_category](tone_letters)

    def disambiguated_rime(
        self,
        parsed: ParsedKuping,
        nucleus: CantoneseConsonant | CantoneseVowel,
        coda: CantoneseConsonant | CantoneseVowel | None,
    ) -> tuple[
        CantoneseConsonant | CantoneseVowel, CantoneseConsonant | CantoneseVowel | None
    ]:
        if parsed.nucleus == "e" and parsed.coda == "i":
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.FRONT,
                rounded=False,
            )
        elif parsed.nucleus == "o" and parsed.coda == "u":
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.BACK,
                rounded=True,
            )
        elif parsed.nucleus == "i" and parsed.coda in ["ŋ", "k"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.NEAR_CLOSE,
                backness=VowelBackness.NEAR_FRONT,
                rounded=False,
            )
        elif parsed.nucleus == "u" and parsed.coda in ["ŋ", "k"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.NEAR_CLOSE,
                backness=VowelBackness.NEAR_BACK,
                rounded=True,
            )
        return nucleus, coda

    def disambiguate_tone(
        self,
        parsed: ParsedKuping,
        syllable: CantoneseSyllable,
        tone: CantoneseTone,
    ) -> tuple[CantoneseSyllable, CantoneseTone]:
        if not isinstance(parsed.tone, str):
            raise ValueError("Tone is not str")
        tone_letters, tone_category = (parsed.tone[:-2] or None), parsed.tone[-2:]
        tone = TONE_TO_OBJECT[tone_category](tone_letters)
        return syllable, tone

    def validity_check(self, parsed: ParsedKuping, reading: CantoneseReading) -> None:
        coda = reading.syllable.final.rime.coda
        coda_is_checked = isinstance(coda, CantoneseConsonant) and coda.checked
        tone_is_entering = reading.tone.name == CantoneseToneName.ENTERING
        if coda_is_checked ^ tone_is_entering:
            raise ValueError(
                f"Invalid {self.name} syllable: {self.compose(parsed)}"
                "Coda does not match tone name"
            )

    def compose(self, uncomposed: ParsedKuping) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone if uncomposed.tone else "",
            ]
        )
