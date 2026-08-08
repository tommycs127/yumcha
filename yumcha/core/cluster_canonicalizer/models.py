"""Data models for grapheme cluster representations.

Provides tuple-based data structures used to create order-invariant keys
for grapheme cluster canonicalization.
"""

from typing import NamedTuple


class ClusterKey(NamedTuple):
    """A canonical, order-invariant representation of a grapheme cluster.

    Attributes:
        base (str): The base character.
        marks (tuple[str, ...]): Combining characters ordered canonically.
    """

    base: str
    marks: tuple[str, ...]
