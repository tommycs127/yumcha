from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from yumcha.phonology import (
    Consonant,
    ConsonantT,
    FinalT,
    ReadingT,
    RimeT,
    SyllableT,
    Tone,
    ToneT,
    Vowel,
    VowelT,
)
from yumcha.schemes.typing import SchemeMap


class RepresentationError(Exception):
    pass


@dataclass(frozen=True)
class ParsedScheme:
    initial: str | None
    medial: str | None
    nucleus: str
    coda: str | None
    tone: str | None


ParsedSchemeT = TypeVar("ParsedSchemeT", bound=ParsedScheme)


class Scheme(
    ABC,
    Generic[
        ConsonantT, VowelT, ToneT, RimeT, FinalT, SyllableT, ReadingT, ParsedSchemeT
    ],
):
    name: str

    @property
    @abstractmethod
    def RIME_CLASS(self) -> type[RimeT]:
        pass

    @property
    @abstractmethod
    def FINAL_CLASS(self) -> type[FinalT]:
        pass

    @property
    @abstractmethod
    def SYLLABLE_CLASS(self) -> type[SyllableT]:
        pass

    @property
    @abstractmethod
    def READING_CLASS(self) -> type[ReadingT]:
        pass

    @property
    @abstractmethod
    def PARSED_CLASS(self) -> type[ParsedSchemeT]:
        pass

    @property
    @abstractmethod
    def MAP(
        self,
    ) -> SchemeMap:
        """
        Maps initials to their respective objects.

        For the dictionary of `object_to_<component>`,
        use `None` as the key for a zero consonant (e.g., `None: "ʔ"`).
        """
        return {
            "initial_to_object": dict(),
            "object_to_initial": dict(),
            "medial_to_object": dict(),
            "object_to_medial": dict(),
            "nucleus_to_object": dict(),
            "object_to_nucleus": dict(),
            "coda_to_object": dict(),
            "object_to_coda": dict(),
            "tone_to_object": dict(),
            "object_to_tone": dict(),
        }

    @abstractmethod
    def get_unnormalized_parsed(self, text: str) -> ParsedSchemeT:
        pass

    def normalize_input(self, parsed: ParsedSchemeT) -> ParsedSchemeT:
        """
        Normalize orthographic variants in the parsed input.

        This stage handles purely spelling-level adjustments, such as:
          - expanding abbreviations,
          - resolving alternate spellings that refer to the same symbol,
          - correcting scheme-specific shorthand,
          - correcting sub-optimal parsed results.
            * only apply this if the error is inherent to the parsing logic.

        It should NOT perform phonological disambiguation.
        Context-based interpretation of symbols (e.g. when a spelling
        represents multiple possible phonological values) should be
        handled in the disambiguation stage.
        """
        return parsed

    def parse(self, text: str) -> ParsedSchemeT:
        unnormalized = self.get_unnormalized_parsed(text)
        return self.normalize_input(unnormalized)

    def get_unprocessed_nucleus(self, parsed: ParsedSchemeT) -> ConsonantT | VowelT:
        return self.MAP["nucleus_to_object"][parsed.nucleus]()

    def get_unprocessed_coda(self, parsed: ParsedSchemeT) -> ConsonantT | VowelT | None:
        return self.MAP["coda_to_object"][parsed.coda]() if parsed.coda else None

    def disambiguate_rime(
        self,
        parsed: ParsedSchemeT,
        nucleus: ConsonantT | VowelT,
        coda: ConsonantT | VowelT | None,
    ) -> tuple[ConsonantT | VowelT, ConsonantT | VowelT | None]:
        """
        Resolve the ambiguity of nucleus and coda here.
        """
        return nucleus, coda

    def get_rime(self, parsed: ParsedSchemeT) -> RimeT:
        nucleus = self.get_unprocessed_nucleus(parsed)
        coda = self.get_unprocessed_coda(parsed)
        nucleus, coda = self.disambiguate_rime(parsed, nucleus, coda)
        return self.RIME_CLASS(nucleus=nucleus, coda=coda)

    def get_unprocessed_medial(self, parsed: ParsedSchemeT) -> VowelT | None:
        return self.MAP["medial_to_object"][parsed.medial]() if parsed.medial else None

    def disambiguate_final(
        self,
        parsed: ParsedSchemeT,
        medial: VowelT | None,
        rime: RimeT,
    ) -> tuple[VowelT | None, RimeT]:
        """
        Resolve the ambiguity of medial and rime here.
        """
        return medial, rime

    def get_final(self, parsed: ParsedSchemeT) -> FinalT:
        medial = self.get_unprocessed_medial(parsed)
        rime = self.get_rime(parsed)
        medial, rime = self.disambiguate_final(parsed, medial, rime)
        return self.FINAL_CLASS(medial=medial, rime=rime)

    def get_unprocessed_initial(self, parsed: ParsedSchemeT) -> ConsonantT | None:
        return (
            self.MAP["initial_to_object"][parsed.initial]() if parsed.initial else None
        )

    def disambiguate_syllable(
        self,
        parsed: ParsedSchemeT,
        initial: ConsonantT | None,
        final: FinalT,
    ) -> tuple[ConsonantT | None, FinalT]:
        """
        Resolve the ambiguity of initial and final here.
        """
        return initial, final

    def get_syllable(self, parsed: ParsedSchemeT) -> SyllableT:
        initial = self.get_unprocessed_initial(parsed)
        final = self.get_final(parsed)
        initial, final = self.disambiguate_syllable(parsed, initial, final)
        return self.SYLLABLE_CLASS(initial=initial, final=final)

    def get_unprocessed_tone(self, parsed: ParsedSchemeT) -> ToneT:
        return self.MAP["tone_to_object"][parsed.tone]()

    def disambiguate_tone(
        self,
        parsed: ParsedSchemeT,
        syllable: SyllableT,
        tone: ToneT,
    ) -> tuple[SyllableT, ToneT]:
        """
        Resolve the ambiguity of syllable and tone here.
        """
        return syllable, tone

    def validity_check(self, parsed: ParsedSchemeT, reading: ReadingT) -> None:
        pass

    def get_reading(self, parsed: ParsedSchemeT) -> ReadingT:
        syllable = self.get_syllable(parsed)
        tone = self.get_unprocessed_tone(parsed)
        syllable, tone = self.disambiguate_tone(parsed, syllable, tone)
        return self.READING_CLASS(syllable=syllable, tone=tone)

    def to_underlying(self, text: str) -> ReadingT:
        parsed = self.parse(text)
        reading = self.get_reading(parsed)
        self.validity_check(parsed, reading)
        return reading

    def get_parsed(self, reading: ReadingT) -> ParsedSchemeT:
        initial = reading.syllable.initial
        medial = reading.syllable.final.medial
        nucleus = reading.syllable.final.rime.nucleus
        coda = reading.syllable.final.rime.coda
        tone = reading.tone

        key_initial = (
            initial.features_signature
            if isinstance(initial, (Consonant, Vowel))
            else None
        )
        key_medial = (
            medial.features_signature
            if isinstance(medial, (Consonant, Vowel))
            else None
        )
        key_nucleus = (
            nucleus.features_signature
            if isinstance(nucleus, (Consonant, Vowel))
            else None
        )
        key_coda = (
            coda.features_signature if isinstance(coda, (Consonant, Vowel)) else None
        )
        key_tone = tone.features_signature if isinstance(nucleus, Tone) else None

        initial = self.MAP["object_to_initial"].get(key_initial, None)
        medial = self.MAP["object_to_medial"].get(key_medial, None)
        nucleus = self.MAP["object_to_nucleus"].get(key_nucleus, None)
        coda = self.MAP["object_to_coda"].get(key_coda, None)
        tone = self.MAP["object_to_tone"].get(key_tone, None)

        if nucleus is None:
            raise ValueError(f"{ReadingT.__name__} object has empty nucleus")

        return self.PARSED_CLASS(
            initial=initial,
            medial=medial,
            nucleus=nucleus,
            coda=coda,
            tone=tone,
        )

    def normalize_output(self, parsed: ParsedSchemeT) -> ParsedSchemeT:
        """
        Apply orthographic rules to the parsed result to be output.
        """
        return parsed

    @abstractmethod
    def compose(self, uncomposed: ParsedSchemeT) -> str:
        pass

    def from_underlying(self, reading: ReadingT) -> str:
        uncomposed = self.get_parsed(reading)
        normalized = self.normalize_output(uncomposed)
        return self.compose(normalized)

    def get_normalized_spelling(
        self,
        initial: str | None,
        medial: str | None,
        nucleus: str,
        coda: str | None,
        tone: str | None,
    ) -> str | None:
        """
        Return the composed spelling when it is valid, otherwise None.

        This method is intended for functions that generates all possible spellings for tests.
        """
        try:
            parsed = self.PARSED_CLASS(
                initial=initial,
                medial=medial,
                nucleus=nucleus,
                coda=coda,
                tone=tone,
            )
            parsed = self.normalize_input(parsed)
            reading = self.get_reading(parsed)
            parsed = self.get_parsed(reading)
            parsed = self.normalize_output(parsed)
            return self.compose(parsed)
        except RepresentationError:
            return None
        except ValueError:
            return None
