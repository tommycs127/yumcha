import csv
import os
from collections.abc import Iterable, Sequence

from .language import Language
from .language.scheme import ValidationError
from .language.scheme.representation import Representation


class Yumcha:
    def __init__(self, languages: Sequence[Language]) -> None:
        self._languages = list(languages)
        self._dictionary = {lang.code: lang for lang in self._languages}
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

    def get_language(self, name: str) -> Language:
        return self._dictionary[name]

    @property
    def menu(self) -> dict[str, list[str]]:
        return self._menu

    def iterate_all_syllables(
        self, language_name: str, scheme_name: str | None = None
    ) -> Iterable[Representation]:
        language = self.get_language(name=language_name.lower())

        if scheme_name is None:
            yield from language.iterate_all_syllables()
        else:
            scheme = language.get_scheme(name=scheme_name.lower())
            yield from scheme.iterate_all_syllables()

    def get_all_syllables(
        self, language_name: str, scheme_name: str | None = None
    ) -> list[Representation]:
        language = self.get_language(name=language_name.lower())

        if scheme_name is None:
            return language.get_all_syllables()
        else:
            scheme = language.get_scheme(name=scheme_name.lower())
            return scheme.get_all_syllables()

    def get_coverage(self, language_name: str, scheme_name: str) -> float:
        language = self.get_language(name=language_name.lower())
        return language.get_coverage(scheme_name=scheme_name.lower())

    def generate_syllable_table(
        self,
        language_name: str,
        file_directory: str,
        file_name: str | None = None,
    ) -> None:
        language = self.get_language(name=language_name.lower())
        if file_name is None:
            file_name = f"{language.code}_syllables"

        file_name = file_name.split(".")[0] + ".tsv"  # Force to be .tsv file
        file_path = os.path.join(file_directory, file_name)

        all_syllables = language.get_all_syllables()

        with open(file_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(["-", *language.schemes, "COUNT"])
            count = {k: 0 for k in language.schemes}
            total_count = 0

            for syllable in all_syllables:
                rows = [syllable]
                total_count += 1

                supported_column_count = 0

                for scheme_name in language.schemes:
                    scheme = language.get_scheme(name=scheme_name)
                    try:
                        representation = scheme.from_intermediate(syllable)
                        representation_roundtrip = scheme.to_intermediate(
                            representation
                        )
                        if representation_roundtrip != syllable:
                            rows.append(
                                f"↦ {representation} [{representation_roundtrip}]"
                            )
                        else:
                            rows.append(representation)
                            count[scheme_name] += 1
                            supported_column_count += 1
                    except ValidationError:  # Representable but disallowed
                        rows.append("⊖")
                    except ValueError:  # Unsupported
                        rows.append("△")

                writer.writerow([*rows, supported_column_count])

            total_label = ["=====", *count.keys(), "TOTAL"]
            total = ["COUNT", *count.values(), total_count]
            writer.writerow(total_label)
            writer.writerow(total)

    def parse(self, language_name: str, scheme_name: str, text: str) -> Representation:
        language = self.get_language(name=language_name.lower())
        scheme = language.get_scheme(name=scheme_name.lower())
        return scheme.parse(text=text)

    def parse_intermediate(
        self, language_name: str, scheme_name: str, text: str
    ) -> Representation:
        language = self.get_language(name=language_name.lower())
        scheme = language.get_scheme(name=scheme_name.lower())
        return scheme.parse_intermediate(text=text)

    def parse_to_intermediate(
        self, language_name: str, scheme_name: str, text: str
    ) -> Representation:
        language = self.get_language(name=language_name.lower())
        scheme = language.get_scheme(name=scheme_name.lower())
        parsed = scheme.parse(text=text)
        return scheme.to_intermediate(parsed=parsed)

    def parse_from_intermediate(
        self, language_name: str, scheme_name: str, text: str
    ) -> Representation:
        language = self.get_language(name=language_name.lower())
        scheme = language.get_scheme(name=scheme_name.lower())
        parsed_intermediate = scheme.parse_intermediate(text=text)
        return scheme.from_intermediate(parsed=parsed_intermediate)

    def convert_as_representation(
        self,
        language_name: str,
        from_scheme_name: str,
        to_scheme_name: str,
        text: str,
    ) -> Representation:
        language = self.get_language(name=language_name.lower())
        from_scheme = language.get_scheme(name=from_scheme_name.lower())
        to_scheme = language.get_scheme(name=to_scheme_name.lower())
        parsed = from_scheme.parse(text=text)
        parsed_intermediate = from_scheme.to_intermediate(parsed=parsed)
        to_scheme_repr = to_scheme.from_intermediate(parsed=parsed_intermediate)
        return to_scheme_repr

    def convert(
        self,
        language_name: str,
        from_scheme_name: str,
        to_scheme_name: str,
        text: str,
    ) -> str:
        return str(
            self.convert_as_representation(
                language_name=language_name,
                from_scheme_name=from_scheme_name,
                to_scheme_name=to_scheme_name,
                text=text,
            )
        )
