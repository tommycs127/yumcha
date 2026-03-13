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
from yumcha.schemes.typing import SchemeMap


class ParsedSLWongPhonetic(ParsedCantoneseScheme):
    pass


class SLWongPhonetic(CantoneseScheme):
    name = "S. L. Wong (Phonetic)"

    @property
    def PARSED_CLASS(self) -> type[ParsedSLWongPhonetic]:
        return ParsedSLWongPhonetic

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

    def get_unnormalized_parsed(self, text: str) -> ParsedSLWongPhonetic:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        tone, initial, nucleus, coda = m.groups()

        return ParsedSLWongPhonetic(
            initial=initial if initial else None,
            medial=None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def disambiguate_rime(
        self,
        parsed: ParsedSLWongPhonetic,
        nucleus: CantoneseConsonant | CantoneseVowel,
        coda: CantoneseConsonant | CantoneseVowel | None,
    ) -> tuple[
        CantoneseConsonant | CantoneseVowel, CantoneseConsonant | CantoneseVowel | None
    ]:
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
        return nucleus, coda

    def disambiguate_tone(
        self,
        parsed: ParsedSLWongPhonetic,
        syllable: CantoneseSyllable,
        tone: CantoneseTone,
    ) -> tuple[CantoneseSyllable, CantoneseTone]:
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
        return syllable, tone

    def compose(self, uncomposed: ParsedSLWongPhonetic) -> str:
        return "".join(
            [
                uncomposed.tone if uncomposed.tone else "",
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
            ]
        )
