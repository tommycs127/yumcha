import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from operator import itemgetter
from typing import Generic, Iterable, get_args

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
        self._dictionary = {obj.name.lower(): obj for obj in self._schemes}
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
                    f"scheme '{scheme.name}' does not meet "
                    f"{self.name.capitalize()} phonology. "
                    f"Add {tuple(sorted(missing_set))} "
                    f"as {scheme.feature_map.key_labels[idx]}"
                )

            if overloaded_set := symbols_set - required_set:
                raise PhonologyError(
                    f"scheme '{scheme.name}' does not meet "
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

    def add(self, scheme_class: type[SchemeT]) -> None:
        scheme = scheme_class(
            intermediate_representation_class=self.intermediate_representation_class
        )
        self.__validate_scheme(scheme)
        self._schemes.append(scheme)

    def get(self, scheme_name: str) -> SchemeT:
        return self._dictionary[scheme_name]

    @property
    def schemes(self) -> list[str]:
        return list(self._dictionary.keys())

    def get_columns(self, iter: Iterable, axis: int) -> list[str]:
        return list(item[axis] for item in iter if item[axis] is not ...)

    def get_columns_by_label(self, iter: Iterable, label: str) -> list[str]:
        axis = self.intermediate_representation_class.get_field_names().index(label)
        return self.get_columns(iter=iter, axis=axis)

    def iterate_all_syllables(self) -> Iterable[IntermediateRepresentationT]:
        symbol_sets: list[list[str]] = [
            sorted(set(self.get_columns_by_label(self.phonology, label)))
            for label in self.intermediate_representation_class.get_field_names()
        ]

        seen = set()

        for combo in itertools.product(*symbol_sets):
            try:
                ipa_representation = (
                    self.intermediate_representation_class.from_features(combo)
                )
                if ipa_representation not in seen:
                    yield ipa_representation
                    seen.add(ipa_representation)
            except ValidationError:
                pass
            except ValueError:
                pass

    def get_all_syllables(self) -> list[IntermediateRepresentationT]:
        return list(self.iterate_all_syllables())
