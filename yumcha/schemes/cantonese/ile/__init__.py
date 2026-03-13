from yumcha.phonology import VowelBackness, VowelCloseness
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseReading,
    CantoneseToneName,
    CantoneseVowel,
)
from yumcha.schemes.cantonese import CantoneseScheme, ParsedCantoneseScheme
from yumcha.schemes.cantonese.ile.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    OBJECT_TO_CODA,
    OBJECT_TO_INITIAL,
    OBJECT_TO_NUCLEUS,
    OBJECT_TO_TONE,
    TONE_TO_OBJECT,
)
from yumcha.schemes.cantonese.ile.regex import REGEX_PATTERN
from yumcha.schemes.typing import SchemeMap


class ParsedILE(ParsedCantoneseScheme):
    pass


class ILE(CantoneseScheme):
    name = "ILE"

    @property
    def PARSED_CLASS(self) -> type[ParsedILE]:
        return ParsedILE

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

    def get_unnormalized_parsed(self, text: str) -> ParsedILE:
        m = REGEX_PATTERN.fullmatch(text)
        if not m:
            raise ValueError(f"Invalid {self.name} syllable: {text}")

        initial, nucleus, coda, tone = m.groups()

        return ParsedILE(
            initial=initial if initial else None,
            medial=None,
            nucleus=nucleus,
            coda=coda if coda else None,
            tone=tone,
        )

    def disambiguate_rime(
        self,
        parsed: ParsedILE,
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
        elif parsed.nucleus == "oe" and parsed.coda in ["y", "n", "t"]:
            nucleus = CantoneseVowel(
                closeness=VowelCloseness.CLOSE_MID,
                backness=VowelBackness.CENTRAL,
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

    def validity_check(self, parsed: ParsedILE, reading: CantoneseReading) -> None:
        coda = reading.syllable.final.rime.coda
        coda_is_checked = isinstance(coda, CantoneseConsonant) and coda.checked
        tone_is_entering = reading.tone.name == CantoneseToneName.ENTERING
        if coda_is_checked ^ tone_is_entering:
            raise ValueError(
                f'Invalid {self.name} syllable "{self.compose(parsed)}": '
                "Coda does not match tone name"
            )

    def compose(self, uncomposed: ParsedILE) -> str:
        return "".join(
            [
                uncomposed.initial if uncomposed.initial else "",
                uncomposed.nucleus,
                uncomposed.coda if uncomposed.coda else "",
                uncomposed.tone if uncomposed.tone else "",
            ]
        )
