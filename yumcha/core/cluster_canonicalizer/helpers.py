"""Helper utilities for Unicode grapheme cluster splitting and key conversion.

Provides functions to decompose NFD-normalized strings into grapheme clusters
and convert clusters into order-invariant `ClusterKey` instances.
"""

import unicodedata

from .models import ClusterKey


def split_clusters(text_nfd: str) -> tuple[str, ...]:
    """Splits an NFD-normalized string into individual grapheme clusters.

    Iterates through the Unicode characters of an NFD string and groups base
    characters (`unicodedata.combining(char) == 0`) with their subsequent
    combining marks.

    Args:
        text_nfd: An NFD (Normalization Form Canonical Decomposition) normalized
            string.

    Returns:
        A tuple of string clusters, where each cluster contains a base character
        followed by its associated combining marks (or leading combining marks
        grouped together if present at the start of the string).
    """
    clusters: list[str] = []
    current = ""
    append = clusters.append

    for char in text_nfd:
        if unicodedata.combining(char) == 0:
            if current:
                append(current)
            current = char
        else:
            if not current:
                current = char
            else:
                current += char

    if current:
        append(current)

    return tuple(clusters)


def to_cluster_key(char: str) -> ClusterKey | None:
    """Converts a grapheme cluster string into a canonical ClusterKey representation.

    Extracts the base character and sorts any attached combining marks lexicographically
    to produce a consistent, order-invariant key representation of the cluster.

    Args:
        char: A string representing a single grapheme cluster (e.g., a base character
            followed by combining marks).

    Returns:
        A `ClusterKey` instance consisting of `(base, marks)` where `base` is the
        base character and `marks` is a tuple of lexicographically sorted combining
        characters, or `None` if the input is empty or starts with a combining mark.
    """
    if char == "":
        return None

    base = char[0]

    if unicodedata.combining(base) != 0:
        return None

    marks = tuple(sorted(char[1:]))
    return ClusterKey(base, marks)
