from yumcha.phonology.cantonese import (
    CantoneseSyllable,
    CantoneseTone,
    CantoneseToneCategory,
    CantoneseToneRegister,
)
from yumcha.schemes.cantonese import CantoneseScheme, ParsedCantoneseScheme
from yumcha.schemes.cantonese.ipa.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.ipa.regex import REGEX_PATTERN
from yumcha.schemes.typing import SchemeMap


class ParsedIPA(ParsedCantoneseScheme):
    pass


class IPA(CantoneseScheme):
    name = "IPA"

    @property
    def PARSED_CLASS(self) -> type[ParsedIPA]:
        return ParsedIPA

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

    def get_unnormalized_parsed(self, text: str) -> ParsedIPA:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        initial, nucleus, coda, tone = m.groups()

        return ParsedIPA(
            initial=initial if initial else None,
            medial=None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def disambiguate_tone(
        self,
        parsed: ParsedIPA,
        syllable: CantoneseSyllable,
        tone: CantoneseTone,
    ) -> tuple[CantoneseSyllable, CantoneseTone]:
        if parsed.tone == "˥" and parsed.coda in ["p̚", "t̚", "k̚"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_UPPER,
                category=CantoneseToneCategory.ENTERING,
            )
        elif parsed.tone == "˧" and parsed.coda in ["p̚", "t̚", "k̚"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.DARK_LOWER,
                category=CantoneseToneCategory.ENTERING,
            )
        elif parsed.tone == "˨" and parsed.coda in ["p̚", "t̚", "k̚"]:
            tone = CantoneseTone(
                register=CantoneseToneRegister.LIGHT,
                category=CantoneseToneCategory.ENTERING,
            )
        return syllable, tone

    def compose(self, uncomposed: ParsedIPA) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone if uncomposed.tone else "",
            ]
        )
