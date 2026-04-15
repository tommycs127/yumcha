import inspect
import itertools
import re
import unicodedata
from abc import ABC, abstractmethod
from collections.abc import Iterable
from functools import cached_property
from typing import get_origin

from .pattern_map import PatternDict, PatternMap
from .representation import Representation, ValidationError


class Scheme[RT: Representation, IRT: Representation](ABC):
    _registry: dict = {}

    def __init__(self, intermediate_representation_class: type[IRT]) -> None:
        self.__intermediate_representation_class: type[IRT] = (
            intermediate_representation_class
        )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        # Find ALL categories this class tries to belong to
        categories = [
            base
            for base in cls.__mro__
            if Scheme in base.__bases__ or get_origin(base) is Scheme
        ]

        if len(categories) > 1:
            raise TypeError(
                f"multi-language schemes are not allowed. "
                f"'{cls.__name__}' attempts to be: {', '.join(c.__name__ for c in categories)}"
            )
        elif len(categories) < 1:
            return

        if (
            (target_category := categories[0])
            and cls is not target_category
            and not inspect.isabstract(cls)
        ):
            Scheme._registry.setdefault(target_category, []).append(cls)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def code(self) -> str:
        return self.name.lower()

    @property
    @abstractmethod
    def representation_class(self) -> type[RT]:
        raise NotImplementedError()

    @property
    def intermediate_representation_class(self) -> type[IRT]:
        return self.__intermediate_representation_class

    @cached_property
    def pattern_map(self) -> PatternMap:
        def _error(exception_type: type[Exception], e: Exception):
            raise exception_type(
                f"invalid map defined for scheme '{self.name}': {str(e)}"
            ) from e

        pattern_map = None

        try:
            pattern_map = PatternMap(
                self.map,
                key_labels=self.intermediate_representation_class.get_field_names(),
                value_labels=self.representation_class.get_field_names(),
                one_way_map=self.one_way_map,
                inverse_map=self.inverse_map,
            )
        except TypeError as te:
            _error(TypeError, te)
        except ValueError as ve:
            _error(ValueError, ve)

        if pattern_map is None:
            raise ValueError("invalid map")

        return pattern_map

    @property
    @abstractmethod
    def map(self) -> PatternDict:
        raise NotImplementedError()

    @property
    def one_way_map(self) -> PatternDict:
        return dict()

    @property
    def inverse_map(self) -> PatternDict:
        return dict()

    def _get_regex_pattern(
        self,
        pattern_map: PatternMap,
        representation_class: type[RT] | type[IRT],
    ) -> str:
        return "".join(
            f"{pattern_map.get_key_regex_pattern(name)}"
            f"{'' if name in representation_class.REQUIRED else '?'}"
            for name in representation_class.get_field_names()
        )

    @cached_property
    def regex_pattern(self) -> str:
        return self._get_regex_pattern(
            pattern_map=self.pattern_map.inverse,
            representation_class=self.representation_class,
        )

    @cached_property
    def intermediate_regex_pattern(self) -> str:
        return self._get_regex_pattern(
            pattern_map=self.pattern_map,
            representation_class=self.intermediate_representation_class,
        )

    def _parse(self, pattern: str, text: str) -> RT:
        decomposed_text = unicodedata.normalize("NFD", text)
        match = re.fullmatch(pattern, decomposed_text)
        if match is None or None in match.groups():
            raise ValueError(f"invalid {self.name} syllable: '{text}'")
        return self.representation_class(**match.groupdict())

    def parse(self, text: str) -> RT:
        return self._parse(self.regex_pattern, text)

    def parse_intermediate(self, text: str) -> RT:
        return self._parse(self.intermediate_regex_pattern, text)

    def to_intermediate(self, parsed: RT) -> IRT:
        inverted = self.pattern_map.inverse.query(parsed.features)
        return self.intermediate_representation_class(*inverted)

    def from_intermediate(self, parsed: IRT) -> RT:
        inverted = self.pattern_map.query(parsed.features)
        return self.representation_class(*inverted)

    def iterate_all_syllables(self) -> Iterable[RT]:
        key_transpose = [sorted(_) for _ in self.pattern_map.key_transpose]

        for combo in itertools.product(*key_transpose):
            try:
                ir = self.intermediate_representation_class.from_features(combo)
                r = self.from_intermediate(ir)
                ir_roundtrip = self.to_intermediate(r)
                if ir == ir_roundtrip:
                    yield r
            except ValidationError:
                pass
            except ValueError:
                pass

    def get_all_syllables(self) -> list[RT]:
        return list(self.iterate_all_syllables())
