from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from phonology import FinalT, ReadingT, RimeT, SyllableT


@dataclass(frozen=True)
class ParsedScheme:
    initial: str | None
    nucleus: str
    coda: str | None
    tone: str | None


ParsedSchemeT = TypeVar("ParsedSchemeT", bound=ParsedScheme)


class Scheme(ABC, Generic[RimeT, FinalT, SyllableT, ReadingT, ParsedSchemeT]):
    name: str

    @abstractmethod
    def parse(self, text: str) -> ParsedSchemeT:
        pass

    def normalize_input(self, parsed: ParsedSchemeT) -> ParsedSchemeT:
        """
        Normalize orthographic variants in the parsed input.

        This stage handles purely spelling-level adjustments, such as:
          - expanding abbreviations,
          - resolving alternate spellings that refer to the same symbol,
          - correcting scheme-specific shorthand,
          - correcting non-ideal parsed result.
            * only do this when the parsed result is inevitable.

        It should NOT perform phonological disambiguation.
        Context-based interpretation of symbols (e.g. when a spelling
        represents multiple possible phonological values) should be
        handled in the disambiguation stage.
        """
        return parsed

    @abstractmethod
    def get_disambiguated_rime(self, parsed: ParsedSchemeT) -> RimeT:
        """
        Resolve the nucleus and coda here.
        """
        pass

    @abstractmethod
    def get_disambiguated_final(self, parsed: ParsedSchemeT) -> FinalT:
        """
        Resolve the medial here.
        Get the rime by calling `self.get_disambiguated_rime()`.
        """
        pass

    @abstractmethod
    def get_disambiguated_syllable(self, parsed: ParsedSchemeT) -> SyllableT:
        """
        Resolve the initial here.
        Get the final by calling `self.get_disambiguated_final()`.
        """
        pass

    @abstractmethod
    def get_disambiguated_reading(self, parsed: ParsedSchemeT) -> ReadingT:
        """
        Resolve the tone here.
        Get the syllable by calling `self.get_disambiguated_syllable()`.
        """
        pass

    def validity_check(self, parsed: ParsedSchemeT, reading: ReadingT) -> None:
        pass

    def to_reading(self, parsed: ParsedSchemeT) -> ReadingT:
        reading = self.get_disambiguated_reading(parsed)
        self.validity_check(parsed, reading)
        return reading

    def to_underlying(self, text: str) -> ReadingT:
        parsed = self.parse(text)
        normalized = self.normalize_input(parsed)
        return self.to_reading(normalized)

    @abstractmethod
    def from_reading(self, reading: ReadingT) -> ParsedSchemeT:
        pass

    def normalize_output(self, parsed: ParsedSchemeT) -> ParsedSchemeT:
        """
        Apply orthographic rules to the parsed result to be output.
        """
        return parsed

    @abstractmethod
    def compose(self, uncomposed: ParsedSchemeT) -> str:
        pass

    def from_underlying(self, reading: ReadingT) -> str:
        uncomposed = self.from_reading(reading)
        normalized = self.normalize_output(uncomposed)
        return self.compose(normalized)
