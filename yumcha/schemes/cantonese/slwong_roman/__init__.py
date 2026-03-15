from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseReading,
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneCategory,
    CantoneseToneRegister,
    CantoneseVowel,
)
from yumcha.schemes import RepresentationError
from yumcha.schemes.cantonese import CantoneseScheme, ParsedCantoneseScheme
from yumcha.schemes.cantonese.slwong_roman.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.slwong_roman.regex import REGEX_PATTERN
from yumcha.schemes.typing import SchemeMap


class ParsedSLWongRoman(ParsedCantoneseScheme):
    pass


class SLWongRoman(CantoneseScheme):
    name = "S. L. Wong (Romanization)"

    @property
    def PARSED_CLASS(self) -> type[ParsedSLWongRoman]:
        return ParsedSLWongRoman

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

    def get_unnormalized_parsed(self, text: str) -> ParsedSLWongRoman:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid SLWong syllable: {text}")

        tone, initial, nucleus, coda = m.groups()

        return ParsedSLWongRoman(
            initial=initial if initial else None,
            medial=None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def normalize_input(self, parsed: ParsedSLWongRoman) -> ParsedSLWongRoman:
        if parsed.nucleus == "aa" and parsed.coda is None:
            raise ValueError(
                f"Invalid {self.name} syllable. "
                f'Did you mean "{parsed.initial}a{parsed.tone}"?'
            )
        elif parsed.nucleus == "a" and parsed.coda is None:
            return ParsedSLWongRoman(
                initial=parsed.initial,
                medial=None,
                nucleus="aa",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "e" and parsed.coda == "ue":
            return ParsedSLWongRoman(
                initial=parsed.initial,
                medial=None,
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

    def disambiguate_rime(
        self,
        parsed: ParsedSLWongRoman,
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
        elif parsed.nucleus == "eu" and parsed.coda in ["ue", "n", "t"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.CENTRAL,
                rounded=True,
            )
        return nucleus, coda

    def disambiguate_tone(
        self,
        parsed: ParsedSLWongRoman,
        syllable: CantoneseSyllable,
        tone: CantoneseTone,
    ) -> tuple[CantoneseSyllable, CantoneseTone]:
        if parsed.tone == "ˈ" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                category=CantoneseToneCategory.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "ˉ" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                category=CantoneseToneCategory.ENTERING,
                letters=tone.letters,
            )
        elif parsed.tone == "ˍ" and parsed.coda in ["p", "t", "k"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                category=CantoneseToneCategory.ENTERING,
                letters=tone.letters,
            )
        return syllable, tone

    def normalize_output(self, parsed: ParsedSLWongRoman) -> ParsedSLWongRoman:
        if parsed.nucleus == "aa" and parsed.coda is None:
            return ParsedSLWongRoman(
                initial=parsed.initial,
                medial=None,
                nucleus="a",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "eu" and parsed.coda == "ue":
            return ParsedSLWongRoman(
                initial=parsed.initial,
                medial=None,
                nucleus="e",
                coda=parsed.coda,
                tone=parsed.tone,
            )
        elif parsed.nucleus == "e" and parsed.coda == "u":
            raise RepresentationError(
                f"The rime {{nucleus={parsed.nucleus}, coda={parsed.coda}}} "
                f"cannot be represented in the {self.name} scheme."
            )

        return parsed

    def compose(self, uncomposed: ParsedSLWongRoman) -> str:
        return "".join(
            [
                uncomposed.tone if uncomposed.tone else "",
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
            ]
        )
