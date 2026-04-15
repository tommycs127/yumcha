import itertools
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from operator import itemgetter
from typing import get_args

from .scheme import Scheme
from .scheme.pattern_map import PatternTuple
from .scheme.representation import Representation, ValidationError


class PhonologyError(Exception):
    pass


type Phonology = tuple[PatternTuple, ...]


@dataclass
class Language[S: Scheme, IRT: Representation](ABC):
    __schemes: list[S] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self._discover()
        self.__dictionary = {obj.code: obj for obj in self.__schemes}

        field_names = self.intermediate_representation_class.get_field_names()
        self.__key_transpose: list[set[str]] = [set() for _ in range(len(field_names))]

        for patterns in self.phonology:
            for idx in range(len(field_names)):
                if (phoneme := patterns[idx]) is not ...:
                    self.__key_transpose[idx].add(phoneme)

        self._validate()

    def _discover(self) -> None:
        # 1. Identify the specific Scheme class from the Generic alias
        # Look at Language[SchemeT] and grabs "SchemeT"
        cls_hierarchy = getattr(self, "__orig_bases__", [])
        if not cls_hierarchy:
            return

        # Get the arguments of the first base class (Language[SchemeT])
        type_args = get_args(cls_hierarchy[0])
        if not type_args:
            return
        target_scheme_base = type_args[0]

        # 2. Dynamic Import (Convention based)
        # Assume the schemes live in: languages.[lang_name].schemes
        try:
            import importlib

            importlib.import_module(f"{self.__class__.__module__}.schemes")
        except ImportError as ie:
            raise RuntimeError(
                f"Language '{self.__class__.__name__.capitalize()}'"
                f"requires a 'schemes' sub-package at {self.__class__.__module__}"
            ) from ie

        # 3. Pull from the registry we built in the previous step
        discovered_classes = Scheme._registry.get(target_scheme_base, [])
        self.__schemes = list(
            cls(
                intermediate_representation_class=self.intermediate_representation_class
            )
            for cls in discovered_classes
        )

    def __validate_scheme(self, scheme: S):
        for idx in range(len(scheme.pattern_map.key_labels)):
            symbols_set = scheme.pattern_map.key_transpose[idx]
            phonology_items = map(itemgetter(idx), self.phonology)
            required_set = set(filter(lambda x: x is not ..., phonology_items))

            if missing_set := required_set - symbols_set:
                raise PhonologyError(
                    f"scheme '{scheme.__class__.__name__}' does not meet "
                    f"{self.name.capitalize()} phonology. "
                    f"Add {tuple(sorted(missing_set))} "
                    f"as {scheme.pattern_map.key_labels[idx]}"
                )

            if overloaded_set := symbols_set - required_set:
                raise PhonologyError(
                    f"scheme '{scheme.__class__.__name__}' does not meet "
                    f"{self.name.capitalize()} phonology. "
                    f"Remove {scheme.pattern_map.key_labels[idx]} "
                    f"{tuple(sorted(overloaded_set))}"
                )

    def _validate(self) -> None:
        if len(self.__schemes) != len(self.__dictionary):
            raise ValueError("scheme names must be unique (case-insensitive)")

        for scheme in self.__schemes:
            self.__validate_scheme(scheme)

        self.validate()

    def validate(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def code(self) -> str:
        return self.name.lower()

    @property
    @abstractmethod
    def intermediate_representation_class(self) -> type[IRT]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def phonology(self) -> tuple[PatternTuple, ...]:
        raise NotImplementedError()

    @property
    def dictionary(self) -> dict[str, S]:
        return self.__dictionary

    def add_scheme(self, scheme_class: type[S]) -> None:
        scheme = scheme_class(
            intermediate_representation_class=self.intermediate_representation_class
        )
        self.__validate_scheme(scheme)
        self.__schemes.append(scheme)

    def get_scheme(self, name: str) -> S:
        return self.__dictionary[name]

    @property
    def schemes(self) -> list[str]:
        return list(self.__dictionary.keys())

    def iterate_all_syllables(self) -> Iterable[IRT]:
        key_transpose = [sorted(_) for _ in self.__key_transpose]
        for combo in itertools.product(*key_transpose):
            try:
                yield self.intermediate_representation_class.from_features(combo)
            except ValidationError:
                pass
            except ValueError:
                pass

    def get_all_syllables(self) -> list[IRT]:
        return list(self.iterate_all_syllables())

    def get_coverage(self, scheme_name: str) -> float:
        all_syllables = self.get_all_syllables()
        scheme_all_syllables = self.get_scheme(name=scheme_name).get_all_syllables()
        return len(scheme_all_syllables) / len(all_syllables)
