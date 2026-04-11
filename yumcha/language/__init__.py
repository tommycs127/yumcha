import itertools
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from operator import itemgetter
from typing import Generic, get_args

from .scheme import Scheme, SchemeT
from .scheme.feature.types import FeatureTuple
from .scheme.representation import IntermediateRepresentationT, ValidationError


class PhonologyError(Exception):
    pass


@dataclass
class Language(ABC, Generic[SchemeT, IntermediateRepresentationT]):
    _schemes: list[SchemeT] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.__discover()
        self._dictionary = {obj.code: obj for obj in self._schemes}
        self.__validate()

    def __discover(self) -> None:
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
        self._schemes = list(
            cls(
                intermediate_representation_class=self.intermediate_representation_class
            )
            for cls in discovered_classes
        )

    def __validate_scheme(self, scheme: SchemeT):
        for idx in range(scheme.feature_map.key_arity):
            symbols_set = set(scheme.feature_map.get_key_columns(idx))
            phonology_items = map(itemgetter(idx), self.phonology)
            required_set = set(filter(lambda x: x is not ..., phonology_items))

            if missing_set := required_set - symbols_set:
                raise PhonologyError(
                    f"scheme '{scheme.__class__.__name__}' does not meet "
                    f"{self.name.capitalize()} phonology. "
                    f"Add {tuple(sorted(missing_set))} "
                    f"as {scheme.feature_map.key_labels[idx]}"
                )

            if overloaded_set := symbols_set - required_set:
                raise PhonologyError(
                    f"scheme '{scheme.__class__.__name__}' does not meet "
                    f"{self.name.capitalize()} phonology. "
                    f"Remove {scheme.feature_map.key_labels[idx]} "
                    f"{tuple(sorted(overloaded_set))}"
                )

    def __validate(self) -> None:
        if len(self._schemes) != len(self._dictionary):
            raise ValueError("scheme names must be unique (case-insensitive)")

        for scheme in self._schemes:
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
    def intermediate_representation_class(self) -> type[IntermediateRepresentationT]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def phonology(self) -> tuple[FeatureTuple, ...]:
        raise NotImplementedError()

    @property
    def dictionary(self) -> dict[str, SchemeT]:
        return self._dictionary

    def add_scheme(self, scheme_class: type[SchemeT]) -> None:
        scheme = scheme_class(
            intermediate_representation_class=self.intermediate_representation_class
        )
        self.__validate_scheme(scheme)
        self._schemes.append(scheme)

    def get_scheme(self, name: str) -> SchemeT:
        return self._dictionary[name]

    @property
    def schemes(self) -> list[str]:
        return list(self._dictionary.keys())

    def _get_phonology_columns_by_label(self, iter: Sequence, label: str) -> list[str]:
        axis = self.intermediate_representation_class.get_field_names().index(label)
        return list(item[axis] for item in iter if item[axis] is not ...)

    def iterate_all_syllables(self) -> Iterable[IntermediateRepresentationT]:
        symbol_sets: list[list[str]] = [
            sorted(set(self._get_phonology_columns_by_label(self.phonology, label)))
            for label in self.intermediate_representation_class.get_field_names()
        ]

        for combo in itertools.product(*symbol_sets):
            try:
                yield self.intermediate_representation_class.from_features(combo)
            except ValidationError:
                pass
            except ValueError:
                pass

    def get_all_syllables(self) -> list[IntermediateRepresentationT]:
        return list(self.iterate_all_syllables())

    def get_coverage(self, scheme_name: str) -> float:
        all_syllables = self.get_all_syllables()
        scheme_all_syllables = self.get_scheme(name=scheme_name).get_all_syllables()
        return len(scheme_all_syllables) / len(all_syllables)
