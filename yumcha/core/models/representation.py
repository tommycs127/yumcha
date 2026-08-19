"""Data representations for phonological features and schemes.

Provides abstract and base dataclass containers for feature structures,
enabling normalized string generation and iteration over field slots.
"""

import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, fields
from typing import ClassVar, override


@dataclass(frozen=True)
class Representation(Iterable[str]):
    """An abstract immutable container representing feature structures.

    Subclasses define fields corresponding to individual features or phonological slots.
    Iterating over a `Representation` yields the value of each field in definition order.
    """

    _SLOT_NAMES: ClassVar[tuple[str, ...]] = ()
    """Class-level attribute populated automatically per concrete subclass"""

    @override
    def __str__(self) -> str:
        """Returns the NFC-normalized string composed by joining all field values.

        Returns:
            A single Unicode string representing the complete phone or sequence.
        """
        return unicodedata.normalize("NFC", "".join(map(str, self)))

    @override
    def __iter__(self) -> Iterator[str]:
        """Iterates through field values in definition order.

        Yields:
            str: The string representation of each feature field value.
        """
        for f in fields(self):
            yield getattr(self, f.name)

    def __getattr__(self, name: str) -> str:
        """Handles lookup attempts for non-existent attributes.

        Args:
            name: The name of the attribute being accessed.

        Raises:
            AttributeError: Always raised with a formatted message indicating the missing attribute.
        """
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute {name!r}"
        )


@dataclass(frozen=True)
class PhonologyRepresentation(Representation):
    """Base class for intermediate phonological feature dataclasses."""


@dataclass(frozen=True)
class SchemeRepresentation(Representation):
    """Base class for scheme-specific feature dataclasses."""
