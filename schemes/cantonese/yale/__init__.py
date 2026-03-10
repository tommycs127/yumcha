import unicodedata

from phonology import VowelBackness, VowelCloseness
from phonology.cantonese import (
    CantoneseFinal,
    CantoneseReading,
    CantoneseRime,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneName,
    CantoneseToneRegister,
    CantoneseVowel,
)
from schemes import ParsedScheme, Scheme
from schemes.cantonese.yale.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from schemes.cantonese.yale.regex import REGEX_PATTERN


class ParsedYale(ParsedScheme):
    initial: str | None
    nucleus: str
    coda: str | None
    tone: str | None


class Yale(
    Scheme[
        CantoneseRime,
        CantoneseFinal,
        CantoneseSyllable,
        CantoneseReading,
        ParsedYale,
    ]
):
    name = "Yale"

    def parse(self, text: str) -> ParsedYale:
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
                nucleus="aa",
                coda=None,
                tone=parsed.tone,
            )
        elif parsed.initial == "y" and parsed.nucleus == "u":
            # Inevitable regex match result correction
            return ParsedYale(
                initial=None,
                nucleus="yu",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        return parsed

    def get_disambiguated_rime(self, parsed: ParsedYale) -> CantoneseRime:
        nucleus = NUCLEUS_TO_OBJECT[parsed.nucleus]()
        coda = CODA_TO_OBJECT[parsed.coda]() if parsed.coda else None
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
        return CantoneseRime(nucleus=nucleus, coda=coda)

    def get_disambiguated_final(self, parsed: ParsedYale) -> CantoneseFinal:
        rime = self.get_disambiguated_rime(parsed)
        return CantoneseFinal(rime=rime, medial=None)

    def get_disambiguated_syllable(self, parsed: ParsedYale) -> CantoneseSyllable:
        final = self.get_disambiguated_final(parsed)
        initial = INITIAL_TO_OBJECT[parsed.initial]() if parsed.initial else None
        return CantoneseSyllable(final=final, initial=initial)

    def get_disambiguated_reading(self, parsed: ParsedYale) -> CantoneseReading:
        syllable = self.get_disambiguated_syllable(parsed)
        tone = TONE_TO_OBJECT[parsed.tone]()
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
        return CantoneseReading(syllable=syllable, tone=tone)

    def from_reading(self, reading: CantoneseReading) -> ParsedYale:
        initial = reading.syllable.initial
        nucleus = reading.syllable.final.rime.nucleus
        coda = reading.syllable.final.rime.coda
        tone = reading.tone
        return ParsedYale(
            initial=OBJECT_TO_INITIAL[
                initial.features_signature if initial is not None else None
            ],
            nucleus=OBJECT_TO_NUCLEUS[nucleus.features_signature],
            coda=OBJECT_TO_CODA[coda.features_signature if coda is not None else None],
            tone=OBJECT_TO_TONE.get(
                tone.features_signature,
                OBJECT_TO_TONE[tone.phonological_signature],
            ),
        )

    def normalize_output(self, parsed: ParsedYale) -> ParsedYale:
        if parsed.nucleus == "aa" and parsed.coda is None:
            return ParsedYale(
                initial=parsed.initial,
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
                    new_nucleus = nucleus + tone[:-1]
                else:
                    new_nucleus = nucleus[0] + tone[:-1] + nucleus[1:]
                if coda in ["", "i", "y", "u"]:
                    new_coda = coda + "h"
                else:
                    new_coda = "h" + coda
            else:
                if nucleus == "yu":
                    new_nucleus = nucleus + tone
                else:
                    new_nucleus = nucleus[0] + tone + nucleus[1:]
                new_coda = coda
            return unicodedata.normalize("NFC", new_nucleus) + new_coda

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
