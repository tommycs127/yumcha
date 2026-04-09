import inspect
import itertools
import re
import unicodedata
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import cached_property
from typing import Generic, Iterable, TypeVar, get_origin

from .feature import FeatureMap
from .feature.types import FeatureDict, FeatureTuple, InverseFeatureDict
from .feature.utils import weak_union_tuples
from .representation import (
    IntermediateRepresentationT,
    RepresentationT,
    ValidationError,
)


class Scheme(ABC, Generic[RepresentationT, IntermediateRepresentationT]):
    _registry: dict = {}
    __intermediate_representation_class: type[IntermediateRepresentationT]

    def __init__(
        self, intermediate_representation_class: type[IntermediateRepresentationT]
    ) -> None:
        self.__intermediate_representation_class = intermediate_representation_class

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
    @abstractmethod
    def representation_class(self) -> type[RepresentationT]:
        raise NotImplementedError()

    @property
    def intermediate_representation_class(self) -> type[IntermediateRepresentationT]:
        return self.__intermediate_representation_class

    @cached_property
    def feature_map(self) -> FeatureMap:
        def _error(exception_type: type[Exception], e: Exception):
            raise exception_type(
                f"invalid map defined for scheme '{self.name}': {str(e)}"
            ) from e

        feature_map = None

        try:
            feature_map = FeatureMap(
                self.map,
                key_labels=self.intermediate_representation_class.get_field_names(),
                value_labels=self.representation_class.get_field_names(),
                inverse_map=self.inverse_map,
            )
        except TypeError as te:
            _error(TypeError, te)
        except ValueError as ve:
            _error(ValueError, ve)

        if feature_map is None:
            raise ValueError("invalid map")

        return feature_map

    @property
    @abstractmethod
    def map(self) -> FeatureDict:
        raise NotImplementedError()

    @property
    def inverse_map(self) -> InverseFeatureDict:
        return dict()

    def _get_regex_pattern(
        self,
        feature_map: FeatureMap,
        representation_class: type[RepresentationT] | type[IntermediateRepresentationT],
    ) -> str:
        return "".join(
            f"{feature_map.get_key_regex_pattern(name)}"
            f"{'' if name in representation_class.REQUIRED else '?'}"
            for name in representation_class.get_field_names()
        )

    def get_regex_pattern(self) -> str:
        return self._get_regex_pattern(
            feature_map=self.feature_map.inverse,
            representation_class=self.representation_class,
        )

    def get_intermediate_regex_pattern(self) -> str:
        return self._get_regex_pattern(
            feature_map=self.feature_map,
            representation_class=self.intermediate_representation_class,
        )

    def _parse(self, pattern: str, text: str) -> RepresentationT:
        decomposed_text = unicodedata.normalize("NFD", text)
        match = re.fullmatch(pattern, decomposed_text)
        if match is None:
            raise ValueError(f'invalid {self.name} syllable: "{text}"')
        return self.representation_class(**match.groupdict())

    def parse(self, text: str) -> RepresentationT:
        return self._parse(self.get_regex_pattern(), text)

    def parse_intermediate(self, text: str) -> RepresentationT:
        return self._parse(self.get_intermediate_regex_pattern(), text)

    def _get_score(self, main_tuple: tuple, comparison_tuple: tuple) -> int:
        score = 0

        for m, c in zip(main_tuple, comparison_tuple):
            if c is ...:
                continue
            if m != c:
                return 0
            score += 1

        return score

    def _get_matched(
        self, rep: RepresentationT | IntermediateRepresentationT, fmap: FeatureMap
    ) -> dict[int, list[FeatureTuple]]:
        matched = defaultdict(list)

        for k in fmap:
            if (score := self._get_score(rep.features, k)) > 0:
                matched[score].append(k)

        return dict(matched)

    def invert(
        self,
        parsed: RepresentationT | IntermediateRepresentationT,
        fmap: FeatureMap,
        backward: bool = False,
    ) -> FeatureTuple:
        fmap = fmap.inverse if backward else fmap
        matched = self._get_matched(parsed, fmap)
        scores = sorted(matched.keys(), reverse=True)
        final_feature = (...,) * fmap.value_arity

        for score in scores:
            for feature in matched[score]:
                if (sym := fmap[feature]) is not None:
                    final_feature = weak_union_tuples(final_feature, sym)

                if ... not in final_feature:
                    return final_feature

        raise ValueError(
            f"incomplete feature {final_feature} inverted from {repr(parsed)}"
        )

    def to_intermediate(self, parsed: RepresentationT) -> IntermediateRepresentationT:
        inverted = self.invert(parsed, self.feature_map, backward=True)
        return self.intermediate_representation_class(*inverted)

    def from_intermediate(self, parsed: IntermediateRepresentationT) -> RepresentationT:
        inverted = self.invert(parsed, self.feature_map)
        return self.representation_class(*inverted)

    def iterate_all_syllables(self) -> Iterable[RepresentationT]:
        """
        Generates all valid syllable combinations.

        Yields:
            RepresentationT: An instance of the representation class
            if it passes validation.
        """

        symbol_sets: list[list[str]] = [
            sorted(set(self.feature_map.get_key_columns(idx)))
            for idx in range(self.feature_map.key_arity)
        ]

        seen = set()

        for combo in itertools.product(*symbol_sets):
            try:
                intermediate_representation = (
                    self.intermediate_representation_class.from_features(combo)
                )
                if (
                    representation := self.from_intermediate(
                        intermediate_representation
                    )
                ) not in seen:
                    yield representation
                    seen.add(representation)
            except ValidationError:
                pass
            except ValueError:
                pass

    def get_all_syllables(self) -> list[RepresentationT]:
        return list(self.iterate_all_syllables())


SchemeT = TypeVar("SchemeT", bound=Scheme)
