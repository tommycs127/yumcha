from typing import Iterable, Sequence

from .language import Language
from .language.scheme.representation import Representation


class Yumcha:
    languages: Sequence[Language] = []

    def __init__(self, languages: Sequence[Language]) -> None:
        if not isinstance(languages, list):
            raise TypeError("not list")

        self.languages = languages.copy()

        if len(self.languages) != len(self.dictionary):
            raise ValueError("language names must be unique (case-insensitive)")

    @property
    def dictionary(self) -> dict[str, Language]:
        return {lang.name.lower(): lang for lang in self.languages}

    def get(self, language_name: str) -> Language:
        return self.dictionary[language_name]

    @property
    def menu(self) -> dict[str, list[str]]:
        return {lang_k: lang_v.menu for lang_k, lang_v in self.dictionary.items()}

    def iterate_all_syllables(
        self, language_name: str, scheme_name: str | None = None
    ) -> Iterable[Representation]:
        language = self.get(language_name=language_name)

        if scheme_name is None:
            yield from language.iterate_all_syllables()
        else:
            scheme = language.get(scheme_name=scheme_name)
            yield from scheme.iterate_all_syllables()

    def get_all_syllables(
        self, language_name: str, scheme_name: str | None = None
    ) -> list[Representation]:
        language = self.get(language_name=language_name)

        if scheme_name is None:
            return language.get_all_syllables()
        else:
            scheme = language.get(scheme_name=scheme_name)
            return scheme.get_all_syllables()

    def parse(self, language_name: str, scheme_name: str, text: str) -> Representation:
        language = self.get(language_name=language_name)
        scheme = language.get(scheme_name=scheme_name)
        return scheme.parse(text=text)

    def parse_ipa(
        self, language_name: str, scheme_name: str, text: str
    ) -> Representation:
        language = self.get(language_name=language_name)
        scheme = language.get(scheme_name=scheme_name)
        return scheme.parse_ipa(text=text)

    def parse_to_ipa(
        self, language_name: str, scheme_name: str, text: str
    ) -> Representation:
        language = self.get(language_name=language_name)
        scheme = language.get(scheme_name=scheme_name)
        parsed = scheme.parse(text=text)
        return scheme.to_ipa(parsed=parsed)

    def parse_from_ipa(
        self, language_name: str, scheme_name: str, text: str
    ) -> Representation:
        language = self.get(language_name=language_name)
        scheme = language.get(scheme_name=scheme_name)
        parsed_ipa = scheme.parse_ipa(text=text)
        return scheme.from_ipa(parsed=parsed_ipa)

    def convert(
        self,
        language_name: str,
        from_scheme_name: str,
        to_scheme_name: str,
        text: str,
        as_str: bool = True,
    ) -> str:
        language = self.get(language_name=language_name)
        from_scheme = language.get(scheme_name=from_scheme_name)
        to_scheme = language.get(scheme_name=to_scheme_name)
        parsed = from_scheme.parse(text=text)
        parsed_ipa = from_scheme.to_ipa(parsed=parsed)
        to_scheme_repr = to_scheme.from_ipa(parsed=parsed_ipa)
        return str(to_scheme_repr) if as_str else to_scheme_repr
