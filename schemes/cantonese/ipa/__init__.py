from phonology.cantonese import (
    CantoneseFinal,
    CantoneseReading,
    CantoneseRime,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneName,
    CantoneseToneRegister,
)
from schemes import ParsedScheme, Scheme
from schemes.cantonese.ipa.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from schemes.cantonese.ipa.regex import REGEX_PATTERN


class ParsedIPA(ParsedScheme):
    initial: str | None
    nucleus: str
    coda: str | None
    tone: str


class IPA(
    Scheme[
        CantoneseRime,
        CantoneseFinal,
        CantoneseSyllable,
        CantoneseReading,
        ParsedIPA,
    ]
):
    name = "IPA"

    def parse(self, text: str) -> ParsedIPA:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        initial, nucleus, coda, tone = m.groups()

        return ParsedIPA(
            initial=initial if initial else None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def get_disambiguated_rime(self, parsed: ParsedIPA) -> CantoneseRime:
        nucleus = NUCLEUS_TO_OBJECT[parsed.nucleus]()
        coda = CODA_TO_OBJECT[parsed.coda]() if parsed.coda else None
        return CantoneseRime(nucleus=nucleus, coda=coda)

    def get_disambiguated_final(self, parsed: ParsedIPA) -> CantoneseFinal:
        rime = self.get_disambiguated_rime(parsed)
        return CantoneseFinal(rime=rime, medial=None)

    def get_disambiguated_syllable(self, parsed: ParsedIPA) -> CantoneseSyllable:
        final = self.get_disambiguated_final(parsed)
        initial = INITIAL_TO_OBJECT[parsed.initial]() if parsed.initial else None
        return CantoneseSyllable(final=final, initial=initial)

    def get_disambiguated_reading(self, parsed: ParsedIPA) -> CantoneseReading:
        syllable = self.get_disambiguated_syllable(parsed)
        tone = TONE_TO_OBJECT[parsed.tone]()
        if parsed.tone == "˥" and parsed.coda in ["p̚", "t̚", "k̚"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "˧" and parsed.coda in ["p̚", "t̚", "k̚"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "˨" and parsed.coda in ["p̚", "t̚", "k̚"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                name=CantoneseToneName.ENTERING,
                letters=tone.letters,
            )
        return CantoneseReading(syllable=syllable, tone=tone)

    def from_reading(self, reading: CantoneseReading) -> ParsedIPA:
        initial = reading.syllable.initial
        nucleus = reading.syllable.final.rime.nucleus
        coda = reading.syllable.final.rime.coda
        tone = reading.tone
        return ParsedIPA(
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

    def compose(self, uncomposed: ParsedIPA) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone,
            ]
        )
