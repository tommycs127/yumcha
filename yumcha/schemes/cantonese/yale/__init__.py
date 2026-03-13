import unicodedata

from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneName,
    CantoneseToneRegister,
    CantoneseVowel,
)
from yumcha.schemes.cantonese import CantoneseScheme, ParsedCantoneseScheme
from yumcha.schemes.cantonese.yale.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.yale.regex import REGEX_PATTERN
from yumcha.schemes.typing import SchemeMap


class ParsedYale(ParsedCantoneseScheme):
    pass


class Yale(CantoneseScheme):
    name = "Yale"

    @property
    def PARSED_CLASS(self) -> type[ParsedYale]:
        return ParsedYale

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

    def get_unnormalized_parsed(self, text: str) -> ParsedYale:
        def parse_nucleus_and_tone(text: str) -> tuple[str, str]:
            nucleus = ""
            tone = ""
            for char in text:
                if unicodedata.category(char) == "Mn":
                    tone += char
                else:
                    nucleus += char
            return nucleus, tone

        # Decompose diacritics
        text = unicodedata.normalize("NFD", text)

        m = REGEX_PATTERN.fullmatch(text)
        if m:
            (
                initial,
                nucleus,
                coda_vowel,
                tone_h,
                coda_consonant,
            ) = m.groups()

            coda_vowel = coda_vowel or ""
            coda_consonant = coda_consonant or ""
            if coda_vowel and coda_consonant:
                raise ValueError(
                    f'Invalid {self.name} syllable "{text}": '
                    "coda must be either a vowel or a consonant, not both"
                )

            coda = coda_vowel or coda_consonant
            nucleus, tone = parse_nucleus_and_tone(nucleus)
            tone += tone_h or ""

            return ParsedYale(
                initial=initial if initial else None,
                medial=None,
                nucleus=nucleus,
                coda=coda if coda else None,
                tone=tone if tone else None,
            )

        raise ValueError(f"Invalid {self.name} syllable: {text}")

    def normalize_input(self, parsed: ParsedYale) -> ParsedYale:
        if parsed.nucleus == "aa" and parsed.coda is None:
            raise ValueError(
                f"Invalid {self.name} syllable. "
                f'Did you mean "{parsed.initial}a{parsed.tone or ""}"?'
            )
        elif parsed.nucleus == "a" and parsed.coda is None:
            return ParsedYale(
                initial=parsed.initial,
                medial=None,
                nucleus="aa",
                coda=None,
                tone=parsed.tone,
            )
        elif parsed.initial == "y" and parsed.nucleus == "u":
            # Inevitable regex match result correction
            return ParsedYale(
                initial=None,
                medial=None,
                nucleus="yu",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        return parsed

    def disambiguate_rime(
        self,
        parsed: ParsedYale,
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
        elif parsed.nucleus == "i" and parsed.coda in ["ng", "k"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.NEAR_CLOSE,
                backness=VowelBackness.NEAR_FRONT,
                rounded=False,
            )
        elif parsed.nucleus == "u" and parsed.coda in ["ng", "k"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.NEAR_CLOSE,
                backness=VowelBackness.NEAR_BACK,
                rounded=True,
            )
        elif parsed.nucleus == "eu":
            if parsed.coda in ["i", "n", "t"]:
                nucleus = CantoneseVowel(
                    closeness=VowelCloseness.CLOSE_MID,
                    backness=VowelBackness.CENTRAL,
                    rounded=True,
                )
            if parsed.coda == "i":
                coda = CantoneseVowel(
                    closeness=VowelCloseness.CLOSE,
                    backness=VowelBackness.FRONT,
                    rounded=True,
                    is_semi=True,
                )
        return nucleus, coda

    def disambiguate_tone(
        self,
        parsed: ParsedYale,
        syllable: CantoneseSyllable,
        tone: CantoneseTone,
    ) -> tuple[CantoneseSyllable, CantoneseTone]:
        if parsed.tone in [chr(0x304), chr(0x300)] and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone is None and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "h" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        return syllable, tone

    def normalize_output(self, parsed: ParsedYale) -> ParsedYale:
        if parsed.nucleus == "aa" and parsed.coda is None:
            return ParsedYale(
                initial=parsed.initial,
                medial=None,
                nucleus="a",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        return parsed

    def compose(self, uncomposed: ParsedYale) -> str:
        def compose_non_initial(
            nucleus: str, coda: str | None, tone: str | None
        ) -> str:
            coda = coda or ""

            if tone is None:
                return nucleus + coda

            if tone.endswith("h"):
                if nucleus == "yu":
                    nucleus += tone[:-1]
                else:
                    nucleus = nucleus[0] + tone[:-1] + nucleus[1:]
                if coda in ["", "i", "y", "u"]:
                    coda += "h"
                else:
                    coda = "h" + coda
            else:
                if nucleus == "yu":
                    nucleus += tone
                else:
                    nucleus = nucleus[0] + tone + nucleus[1:]
            return unicodedata.normalize("NFC", nucleus) + coda

        uncomposed_non_initial = compose_non_initial(
            nucleus=uncomposed.nucleus,
            coda=uncomposed.coda,
            tone=uncomposed.tone,
        )

        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed_non_initial,
            ]
        )
