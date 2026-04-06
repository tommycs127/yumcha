import unicodedata
from dataclasses import astuple, dataclass, fields
from functools import cache
from typing import ClassVar, Self, TypeVar


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class Representation:
    REQUIRED: ClassVar[tuple[()] | tuple[str, ...]] = tuple()

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        pass

    @property
    def features(self) -> tuple[str, ...]:
        return astuple(self)

    @classmethod
    def from_features(cls, features: tuple) -> Self:
        return cls(*features)

    @classmethod
    @cache
    def get_field_names(cls) -> tuple[str, ...]:
        return tuple(field.name for field in fields(cls))

    @cache
    def get_string(self, raw: bool = False) -> str:
        uncomposed_text = "".join(
            getattr(self, field.name) or "" for field in fields(self)
        )
        if raw:
            return uncomposed_text
        return unicodedata.normalize("NFC", uncomposed_text)

    def __str__(self) -> str:
        return self.get_string()


RepresentationT = TypeVar("RepresentationT", bound=Representation)
IPARepresentationT = TypeVar("IPARepresentationT", bound=Representation)
