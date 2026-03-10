from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseFinal,
    CantoneseReading,
    CantoneseRime,
    CantoneseSyllable,
    CantoneseToneName,
    CantoneseVowel,
)
from yumcha.schemes import ParsedScheme, Scheme
from yumcha.schemes.cantonese.slwong.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.slwong.regex import REGEX_PATTERN


class ParsedSLWong(ParsedScheme):
    initial: str | None
    nucleus: str
    coda: str | None
    tone: str


class SLWong(
    Scheme[
        CantoneseRime,
        CantoneseFinal,
        CantoneseSyllable,
        CantoneseReading,
        ParsedSLWong,
    ]
):
    name = "S. L. Wong"

    def parse(self, text: str) -> ParsedSLWong:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid SLWong syllable: {text}")

        initial, nucleus, coda, tone = m.groups()

        return ParsedSLWong(
            initial=initial if initial else None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def normalize_input(self, parsed: ParsedSLWong) -> ParsedSLWong:
        if parsed.nucleus == "aa" and parsed.coda is None:
            raise ValueError(
                f"Invalid {self.name} syllable. "
                f'Did you mean "{parsed.initial}a{parsed.tone}"?'
            )
        elif parsed.nucleus == "a" and parsed.coda is None:
            return ParsedSLWong(
                initial=parsed.initial, nucleus="aa", coda=parsed.coda, tone=parsed.tone
            )
        elif parsed.nucleus == "e" and parsed.coda == "ue":
            return ParsedSLWong(
                initial=parsed.initial,
                nucleus="eu",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "e" and parsed.coda == "u":
            raise ValueError(
                f"Invalid {self.name} orthographic combination: "
                f"(nucleus={parsed.nucleus}, coda={parsed.coda})"
            )
        return parsed

    def get_disambiguated_rime(self, parsed: ParsedSLWong) -> CantoneseRime:
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
        elif parsed.nucleus == "eu" and parsed.coda in ["ue", "n", "t"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.CENTRAL,
                rounded=True,
            )
        return CantoneseRime(nucleus=nucleus, coda=coda)

    def get_disambiguated_final(self, parsed: ParsedSLWong) -> CantoneseFinal:
        rime = self.get_disambiguated_rime(parsed)
        return CantoneseFinal(rime=rime, medial=None)

    def get_disambiguated_syllable(self, parsed: ParsedSLWong) -> CantoneseSyllable:
        final = self.get_disambiguated_final(parsed)
        initial = INITIAL_TO_OBJECT[parsed.initial]() if parsed.initial else None
        return CantoneseSyllable(final=final, initial=initial)

    def get_disambiguated_reading(self, parsed: ParsedSLWong) -> CantoneseReading:
        syllable = self.get_disambiguated_syllable(parsed)
        tone = TONE_TO_OBJECT[parsed.tone]()
        return CantoneseReading(syllable=syllable, tone=tone)

    def validity_check(self, parsed: ParsedSLWong, reading: CantoneseReading) -> None:
        coda = reading.syllable.final.rime.coda
        coda_is_checked = isinstance(coda, CantoneseConsonant) and coda.checked
        tone_is_entering = reading.tone.name == CantoneseToneName.ENTERING
        if coda_is_checked ^ tone_is_entering:
            raise ValueError(
                f"Invalid {self.name} syllable: {self.compose(parsed)}"
                "Coda does not match tone name"
            )

    def from_reading(self, reading: CantoneseReading) -> ParsedSLWong:
        initial = reading.syllable.initial
        nucleus = reading.syllable.final.rime.nucleus
        coda = reading.syllable.final.rime.coda
        tone = reading.tone
        return ParsedSLWong(
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

    def normalize_output(self, parsed: ParsedSLWong) -> ParsedSLWong:
        if parsed.nucleus == "aa" and parsed.coda is None:
            return ParsedSLWong(
                initial=parsed.initial,
                nucleus="a",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "eu" and parsed.coda == "ue":
            return ParsedSLWong(
                initial=parsed.initial,
                nucleus="e",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "e" and parsed.coda == "u":
            raise ValueError(
                f"The reading {{nucleus={parsed.nucleus}, coda={parsed.coda}}} "
                f"cannot be represented in the {self.name} scheme."
            )

        return parsed

    def compose(self, uncomposed: ParsedSLWong) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone,
            ]
        )
