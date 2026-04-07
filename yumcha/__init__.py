from collections.abc import Iterable, Sequence

from .language import Language
from .language.scheme.representation import Representation


class Yumcha:
    def __init__(self, languages: Sequence[Language]) -> None:
        self._languages = list(languages)
        self._dictionary = {lang.name.lower(): lang for lang in self._languages}
        self._menu = {
            lang_k: lang_v.schemes for lang_k, lang_v in self._dictionary.items()
        }
        if len(self._languages) != len(self._dictionary):
            raise ValueError("language names must be unique (case-insensitive)")

    @property
    def languages(self) -> list[Language]:
        return self._languages

    @property
    def dictionary(self) -> dict[str, Language]:
        return self._dictionary

    def get(self, language_name: str) -> Language:
        return self._dictionary[language_name]

    @property
    def menu(self) -> dict[str, list[str]]:
        return self._menu

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

    def get_coverage(self, language_name: str, scheme_name: str) -> float:
        langauge_all_syllables_count = len(
            self.get_all_syllables(language_name=language_name)
        )
        scheme_all_syllables_count = len(
            self.get_all_syllables(language_name=language_name, scheme_name=scheme_name)
        )
        return scheme_all_syllables_count / langauge_all_syllables_count

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
    ) -> str | Representation:
        language = self.get(language_name=language_name)
        from_scheme = language.get(scheme_name=from_scheme_name)
        to_scheme = language.get(scheme_name=to_scheme_name)
        parsed = from_scheme.parse(text=text)
        parsed_ipa = from_scheme.to_ipa(parsed=parsed)
        to_scheme_repr = to_scheme.from_ipa(parsed=parsed_ipa)
        return str(to_scheme_repr) if as_str else to_scheme_repr
