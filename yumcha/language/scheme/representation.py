import unicodedata
from dataclasses import astuple, dataclass, fields
from functools import cache
from typing import ClassVar, Self

from .pattern_tuple import PatternTuple

MISSING = object()


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class Representation:
    REQUIRED: ClassVar[tuple[()] | tuple[str, ...]] = tuple()

    def __post_init__(self) -> None:
        for required_field in self.REQUIRED:
            value = getattr(self, required_field, MISSING)
            if value is MISSING:
                raise ValidationError(
                    f"invalid value for field '{required_field}'. Expected str, got '{value}'"
                )

        self.validate()

    def validate(self) -> None:
        pass

    @property
    def patterns(self) -> PatternTuple:
        return PatternTuple(astuple(self))

    @classmethod
    def from_patterns(cls, patterns: tuple[str, ...]) -> Self:
        for pattern in patterns:
            if not isinstance(pattern, str):
                raise TypeError(f"expected str, got {type(pattern).__name__}")
        return cls(*patterns)

    @classmethod
    @cache
    def get_field_names(cls) -> tuple[str, ...]:
        return tuple(field.name for field in fields(cls))

    @cache
    def get_string(self, raw: bool = False) -> str:
        field_names = self.get_field_names()
        uncomposed_text = "".join(getattr(self, name) or "" for name in field_names)
        if raw:
            return uncomposed_text
        return unicodedata.normalize("NFC", uncomposed_text)

    def __str__(self) -> str:
        return self.get_string()

    def __len__(self) -> int:
        return len(self.get_string())
