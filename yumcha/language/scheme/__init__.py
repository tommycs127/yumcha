import inspect
import itertools
import re
import unicodedata
from abc import ABC, abstractmethod
from collections.abc import Iterable
from functools import cached_property
from typing import get_origin

from .pattern_map import PatternMap
from .representation import Representation, ValidationError
from .schema import PatternRegistry


class Scheme[RT: Representation, IRT: Representation](ABC):
    _registry: dict = {}

    def __init__(self, intermediate_representation_class: type[IRT]) -> None:
        self.__intermediate_representation_class: type[IRT] = (
            intermediate_representation_class  # For Language.add_scheme to set class
        )

        if not issubclass(self.representation_class, Representation):
            raise TypeError(
                f"{self.name}.representation_class must be a subclass of Representation"
            )

        if not issubclass(self.intermediate_representation_class, Representation):
            raise TypeError(
                f"{self.name}.intermediate_representation_class "
                "must be a subclass of Representation"
            )

        # Schema flattening

        label_schema_keys = tuple(self.label_schema.keys())

        label_schema_values_raw = [
            value for values in self.label_schema.values() for value in values
        ]
        label_schema_values = tuple(dict.fromkeys(label_schema_values_raw))

        # Labels validation

        irc_field_names = self.intermediate_representation_class.get_field_names()
        rc_field_names = self.representation_class.get_field_names()

        label_schema_keys_set = set(label_schema_keys)
        label_schema_values_set = set(label_schema_values)
        irc_field_names_set = set(irc_field_names)
        rc_field_names_set = set(rc_field_names)

        def _validate_sets_match(
            actual_set: set, expected_set: set, context_name: str, class_obj: type
        ):
            if actual_set == expected_set:
                return

            msg = (
                f"{context_name} do not match the field names "
                f"in {class_obj.__name__} class"
            )

            parts = [msg]
            if extra := actual_set - expected_set:
                parts.append(f"Remove {extra}")
            if missing := expected_set - actual_set:
                parts.append(f"Add {missing}")

            raise ValueError(". ".join(parts))

        _validate_sets_match(
            actual_set=label_schema_keys_set,
            expected_set=irc_field_names_set,
            context_name="keys of label schema",
            class_obj=self.intermediate_representation_class,
        )

        _validate_sets_match(
            actual_set=label_schema_values_set,
            expected_set=rc_field_names_set,
            context_name="values of label schema",
            class_obj=self.representation_class,
        )

        label_indexes_list = [
            tuple(rc_field_names.index(value) for value in values)
            for values in self.label_schema.values()
        ]

        # Storing variables

        self.__label_schema_keys: tuple[str, ...] = label_schema_keys
        self.__label_schema_values: tuple[str, ...] = label_schema_values

        try:
            self.__pattern_map: PatternMap = PatternMap(
                self.map,
                key_tuple_length=len(label_schema_keys),
                value_tuple_length=len(label_schema_values),
                label_indexes_list=label_indexes_list,
                one_way_map=self.one_way_map,
                inverse_map=self.inverse_map,
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"invalid map defined for scheme '{self.name}'") from e

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
                f"'{cls.__name__}' attempts to be: "
                f"{', '.join(c.__name__ for c in categories)}"
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
    @abstractmethod
    def intermediate_representation_class(self) -> type[IRT]:
        try:
            return self.__intermediate_representation_class
        except AttributeError as ae:
            raise NotImplementedError(
                f"'{self.name}' has no intermediate_representation_class. "
                "Ensure it is passed to __init__ or registered "
                "via a Language instance."
            ) from ae

    @property
    @abstractmethod
    def label_schema(self) -> dict[str, tuple[str, ...]]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def map(self) -> PatternRegistry:
        raise NotImplementedError()

    @property
    def one_way_map(self) -> PatternRegistry:
        return dict()

    @property
    def inverse_map(self) -> PatternRegistry:
        return dict()

    @property
    def label_schema_keys(self) -> tuple[str, ...]:
        return self.__label_schema_keys

    @property
    def label_schema_values(self) -> tuple[str, ...]:
        return self.__label_schema_values

    @property
    def pattern_map(self) -> PatternMap:
        return self.__pattern_map

    def _get_regex_pattern(
        self, pattern_map: PatternMap, representation_class: type[RT] | type[IRT]
    ) -> str:
        field_names = representation_class.get_field_names()
        groups = []

        for idx, field_name in enumerate(field_names):
            key_transpose_set = sorted(
                pattern_map.get_key_transpose_set(idx),
                key=len,
                reverse=True,
            )

            pattern = "|".join(re.escape(s) for s in key_transpose_set)
            suffix = "" if field_name in representation_class.REQUIRED else "?"
            group = f"(?P<{field_name}>{pattern}){suffix}"

            groups.append(group)

        return "".join(groups)

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

    def _parse_to_class[T: Representation](
        self, text: str, pattern: str, cls: type[T]
    ) -> T:
        decomposed_text = unicodedata.normalize("NFD", text)
        match = re.fullmatch(pattern, decomposed_text)

        if match is None or None in match.groups():
            raise ValueError(f"invalid {self.name} syllable: '{text}'")

        return cls(**match.groupdict())

    def parse(self, text: str) -> RT:
        return self._parse_to_class(
            text=text,
            pattern=self.regex_pattern,
            cls=self.representation_class,
        )

    def parse_intermediate(self, text: str) -> IRT:
        return self._parse_to_class(
            text=text,
            pattern=self.intermediate_regex_pattern,
            cls=self.intermediate_representation_class,
        )

    def to_intermediate(self, parsed: RT) -> IRT:
        inverted = self.pattern_map.inverse.query(parsed.patterns)
        return self.intermediate_representation_class(*inverted)

    def from_intermediate(self, parsed: IRT) -> RT:
        inverted = self.pattern_map.query(parsed.patterns)
        return self.representation_class(*inverted)

    def iterate_all_syllables(self) -> Iterable[RT]:
        key_transpose = [sorted(_) for _ in self.pattern_map.keys_transpose_set]

        for combo in itertools.product(*key_transpose):
            try:
                ir = self.intermediate_representation_class.from_patterns(combo)
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
