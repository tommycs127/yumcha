from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseFinal,
    CantoneseReading,
    CantoneseRime,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneName,
    CantoneseToneRegister,
    CantoneseVowel,
)
from yumcha.schemes import ParsedScheme, Scheme
from yumcha.schemes.cantonese.sidneylau.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.sidneylau.regex import REGEX_PATTERN


class ParsedSidneyLau(ParsedScheme):
    initial: str | None
    nucleus: str
    coda: str | None
    tone: str


class SidneyLau(
    Scheme[
        CantoneseRime,
        CantoneseFinal,
        CantoneseSyllable,
        CantoneseReading,
        ParsedSidneyLau,
    ]
):
    name = "Sidney Lau"

    def parse(self, text: str) -> ParsedSidneyLau:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        initial, nucleus, coda, tone = m.groups()

        return ParsedSidneyLau(
            initial=initial if initial else None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def normalize_input(self, parsed: ParsedSidneyLau) -> ParsedSidneyLau:
        if parsed.nucleus == "aa" and parsed.coda is None:
            raise ValueError(
                f"Invalid {self.name} syllable. "
                f'Did you mean "{parsed.initial}a{parsed.tone}"?'
            )
        elif parsed.nucleus == "o" and parsed.coda == "u":
            raise ValueError(
                f"Invalid {self.name} syllable. "
                f'Did you mean "{parsed.initial}o{parsed.tone}"?'
            )
        elif parsed.nucleus == "a" and parsed.coda is None:
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus="aa",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "o" and parsed.coda is not None:
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus="oh",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "eu" and parsed.coda is not None:
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus="euh",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        return parsed

    def get_disambiguated_rime(self, parsed: ParsedSidneyLau) -> CantoneseRime:
        nucleus = NUCLEUS_TO_OBJECT[parsed.nucleus]()
        coda = CODA_TO_OBJECT[parsed.coda]() if parsed.coda else None
        if parsed.nucleus == "e" and parsed.coda == "i":
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.FRONT,
                rounded=False,
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
        elif parsed.nucleus == "u" and parsed.coda == "i":
            coda = CantoneseVowel(
                closeness=VowelCloseness.CLOSE,
                backness=VowelBackness.FRONT,
                rounded=True,
                is_semi=True,
            )
        elif parsed.nucleus == "o" and parsed.coda is None:
            coda = CantoneseVowel(
                closeness=VowelCloseness.CLOSE,
                backness=VowelBackness.BACK,
                rounded=True,
                is_semi=True,
            )
        return CantoneseRime(nucleus=nucleus, coda=coda)

    def get_disambiguated_final(self, parsed: ParsedSidneyLau) -> CantoneseFinal:
        rime = self.get_disambiguated_rime(parsed)
        return CantoneseFinal(rime=rime, medial=None)

    def get_disambiguated_syllable(self, parsed: ParsedSidneyLau) -> CantoneseSyllable:
        final = self.get_disambiguated_final(parsed)
        initial = INITIAL_TO_OBJECT[parsed.initial]() if parsed.initial else None
        return CantoneseSyllable(final=final, initial=initial)

    def get_disambiguated_reading(self, parsed: ParsedSidneyLau) -> CantoneseReading:
        syllable = self.get_disambiguated_syllable(parsed)
        tone = TONE_TO_OBJECT[parsed.tone]()
        if parsed.tone == "1" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "3" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "6" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        return CantoneseReading(syllable=syllable, tone=tone)

    def from_reading(self, reading: CantoneseReading) -> ParsedSidneyLau:
        initial = reading.syllable.initial
        nucleus = reading.syllable.final.rime.nucleus
        coda = reading.syllable.final.rime.coda
        tone = reading.tone
        return ParsedSidneyLau(
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

    def normalize_output(self, parsed: ParsedSidneyLau) -> ParsedSidneyLau:
        if parsed.nucleus == "aa" and parsed.coda is None:
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus="a",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "oh" and parsed.coda is not None:
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus="o",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "euh" and parsed.coda is not None:
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus="eu",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "o" and parsed.coda == "u":
            return ParsedSidneyLau(
                initial=parsed.initial,
                nucleus=parsed.nucleus,
                coda=None,
                tone=parsed.tone,
            )
        return parsed

    def compose(self, uncomposed: ParsedSidneyLau) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone,
            ]
        )
