from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseFinal,
    CantoneseReading,
    CantoneseRime,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseVowel,
)
from yumcha.schemes import ParsedScheme, ParsedSchemeT, Scheme


class ParsedCantoneseScheme(ParsedScheme):
    initial: str | None
    medial: None
    nucleus: str
    coda: str | None
    tone: str | None


class CantoneseScheme(
    Scheme[
        CantoneseConsonant,
        CantoneseVowel,
        CantoneseTone,
        CantoneseRime,
        CantoneseFinal,
        CantoneseSyllable,
        CantoneseReading,
        ParsedSchemeT,
    ]
):
    @property
    def RIME_CLASS(self) -> type[CantoneseRime]:
        return CantoneseRime

    @property
    def FINAL_CLASS(self) -> type[CantoneseFinal]:
        return CantoneseFinal

    @property
    def SYLLABLE_CLASS(self) -> type[CantoneseSyllable]:
        return CantoneseSyllable

    @property
    def READING_CLASS(self) -> type[CantoneseReading]:
        return CantoneseReading
