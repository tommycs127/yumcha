from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneCategory,
    CantoneseToneRegister,
    CantoneseVowel,
)
from yumcha.schemes.cantonese import CantoneseScheme, ParsedCantoneseScheme
from yumcha.schemes.cantonese.jyutping.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.jyutping.regex import REGEX_PATTERN
from yumcha.schemes.typing import SchemeMap


class ParsedJyutping(ParsedCantoneseScheme):
    pass


class Jyutping(CantoneseScheme):
    name = "Jyutping"

    @property
    def PARSED_CLASS(self) -> type[ParsedJyutping]:
        return ParsedJyutping

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

    def get_unnormalized_parsed(self, text: str) -> ParsedJyutping:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        initial, nucleus, coda, tone = m.groups()

        return ParsedJyutping(
            initial=initial if initial else None,
            medial=None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def disambiguate_rime(
        self,
        parsed: ParsedJyutping,
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
        elif parsed.nucleus == "eo" and parsed.coda == "i":
            coda = CantoneseVowel(
                closeness=VowelCloseness.CLOSE,
                backness=VowelBackness.FRONT,
                rounded=True,
                is_semi=True,
            )
        return nucleus, coda

    def disambiguate_tone(
        self,
        parsed: ParsedJyutping,
        syllable: CantoneseSyllable,
        tone: CantoneseTone,
    ) -> tuple[CantoneseSyllable, CantoneseTone]:
        if parsed.tone == "1" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                category=CantoneseToneCategory.ENTERING,
            )
        elif parsed.tone == "3" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                category=CantoneseToneCategory.ENTERING,
            )
        elif parsed.tone == "6" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                category=CantoneseToneCategory.ENTERING,
            )
        return syllable, tone

    def compose(self, uncomposed: ParsedJyutping) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone if uncomposed.tone else "",
            ]
        )
