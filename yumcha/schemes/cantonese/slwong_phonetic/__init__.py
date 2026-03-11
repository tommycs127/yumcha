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
from yumcha.schemes.cantonese.slwong_phonetic.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.slwong_phonetic.regex import REGEX_PATTERN


class ParsedSLWongPhonetic(ParsedScheme):
    initial: str | None
    nucleus: str
    coda: str | None
    tone: str


class SLWongPhonetic(
    Scheme[
        CantoneseRime,
        CantoneseFinal,
        CantoneseSyllable,
        CantoneseReading,
        ParsedSLWongPhonetic,
    ]
):
    name = "S. L. Wong (Phonetic)"

    def parse(self, text: str) -> ParsedSLWongPhonetic:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        tone, initial, nucleus, coda = m.groups()

        return ParsedSLWongPhonetic(
            initial=initial if initial else None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def get_disambiguated_rime(self, parsed: ParsedSLWongPhonetic) -> CantoneseRime:
        nucleus = NUCLEUS_TO_OBJECT[parsed.nucleus]()
        coda = CODA_TO_OBJECT[parsed.coda]() if parsed.coda else None
        if parsed.nucleus == "œ" and parsed.coda in ["n", "t"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.CENTRAL,
                rounded=True,
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
        return CantoneseRime(nucleus=nucleus, coda=coda)

    def get_disambiguated_final(self, parsed: ParsedSLWongPhonetic) -> CantoneseFinal:
        rime = self.get_disambiguated_rime(parsed)
        return CantoneseFinal(rime=rime, medial=None)

    def get_disambiguated_syllable(
        self, parsed: ParsedSLWongPhonetic
    ) -> CantoneseSyllable:
        final = self.get_disambiguated_final(parsed)
        initial = INITIAL_TO_OBJECT[parsed.initial]() if parsed.initial else None
        return CantoneseSyllable(final=final, initial=initial)

    def get_disambiguated_reading(
        self, parsed: ParsedSLWongPhonetic
    ) -> CantoneseReading:
        syllable = self.get_disambiguated_syllable(parsed)
        tone = TONE_TO_OBJECT[parsed.tone]()
        if parsed.tone == "ˈ" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "ˉ" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "ˍ" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        return CantoneseReading(syllable=syllable, tone=tone)

    def from_reading(self, reading: CantoneseReading) -> ParsedSLWongPhonetic:
        initial = reading.syllable.initial
        nucleus = reading.syllable.final.rime.nucleus
        coda = reading.syllable.final.rime.coda
        tone = reading.tone
        return ParsedSLWongPhonetic(
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

    def compose(self, uncomposed: ParsedSLWongPhonetic) -> str:
        return "".join(
            [
                uncomposed.tone,
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
            ]
        )
