"""Unicode grapheme cluster canonicalizer.

Learns preferred combining mark ordering from training datasets and
reorders combining marks within grapheme clusters into canonical representations.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from types import MappingProxyType
from typing import TYPE_CHECKING

from .helpers import split_clusters, to_cluster_key

if TYPE_CHECKING:
    from .models import ClusterKey

INF = float("inf")


class ClusterCanonicalizer:
    """Learns combining mark ordering rules and normalizes grapheme clusters.

    `ClusterCanonicalizer` ingests character sets to learn valid combining mark
    orders per base character and individual mark position ranks. It then applies
    these rules to reorder multi-mark grapheme clusters consistently.
    """

    def __init__(self) -> None:
        """Initializes an empty ClusterCanonicalizer instance."""
        self._cluster_map: dict[ClusterKey, str] = {}
        self._mark_rank: dict[str, int] = {}

        self._cluster_map_view: MappingProxyType[ClusterKey, str] = MappingProxyType(
            self._cluster_map
        )
        self._mark_rank_view: MappingProxyType[str, int] = MappingProxyType(
            self._mark_rank
        )

    @property
    def cluster_map(self) -> MappingProxyType[ClusterKey, str]:
        """MappingProxyType[ClusterKey, str]: Immutable view of learned ClusterKey-to-canonical-string mappings."""
        return self._cluster_map_view

    @property
    def mark_rank(self) -> MappingProxyType[str, int]:
        """MappingProxyType[str, int]: Immutable view of learned combining mark positional rankings."""
        return self._mark_rank_view

    def learn(self, charsets: Iterable[Iterable[str]]) -> None:
        """Learns cluster structures and mark orderings from unnormalized character sets.

        Normalizes tokens to NFD before processing cluster orderings.

        Args:
            charsets: An iterable of character sets (collections of strings).
        """
        charsets_norm = [
            {unicodedata.normalize("NFD", token) for token in charset}
            for charset in charsets
        ]
        self.learn_from_nfd(charsets_norm)

    def learn_from_nfd(self, charsets_nfd: Iterable[Iterable[str]]) -> None:
        """Learns cluster structures and mark orderings directly from NFD-normalized character sets.

        Args:
            charsets_nfd: An iterable of NFD-normalized character sets.
        """
        self._learn_ordering(charsets_nfd)
        self._learn_mark_rank()

    def _learn_ordering(self, charsets_nfd: Iterable[Iterable[str]]) -> None:
        """Extracts and registers canonical cluster strings from NFD character sets.

        Args:
            charsets_nfd: An iterable of NFD-normalized character sets.

        Raises:
            ValueError: If a cluster key maps to two conflicting cluster representations.
        """
        seen_sources: dict[ClusterKey, str] = {}
        _cluster_map = self._cluster_map

        for charset in charsets_nfd:
            for token in charset:
                for cluster in split_clusters(token):
                    key = to_cluster_key(cluster)
                    if key is None:
                        continue

                    learned_key = _cluster_map.get(key)
                    if learned_key is None:
                        _cluster_map[key] = cluster
                        seen_sources[key] = token
                    elif learned_key != cluster:
                        raise ValueError(
                            "conflicting canonical cluster order for "
                            f"{key}: {learned_key!r} (from {seen_sources[key]!r}) "
                            f"vs {cluster!r} (from {token!r})"
                        )

    def _learn_mark_rank(self) -> None:
        """Computes the minimum positional index rank for each combining mark in valid learned clusters.

        Clusters starting with a combining mark are skipped.
        """
        _cluster_map = self._cluster_map
        _mark_rank = self._mark_rank

        for cluster in _cluster_map.values():
            base = cluster[0]
            if unicodedata.combining(base) != 0:
                continue

            marks = cluster[1:]
            for pos, mark in enumerate(marks):
                old_rank = _mark_rank.get(mark)
                if old_rank is None or pos < old_rank:
                    _mark_rank[mark] = pos

    def canonicalize(self, text: str) -> str:
        """Reorders combining marks in a string to match learned canonical orders.

        Normalizes input string to NFD format before processing.

        Args:
            text: Input string to canonicalize.

        Returns:
            The canonicalized string in NFD form with combining marks reordered.
        """
        text_nfd = unicodedata.normalize("NFD", text)
        return self.canonicalize_from_nfd(text_nfd)

    def canonicalize_from_nfd(self, text_nfd: str) -> str:
        """Reorders combining marks in an NFD-normalized string using learned cluster rules.

        Args:
            text_nfd: An NFD-normalized input string.

        Returns:
            The string with all constituent grapheme clusters reordered canonically.
        """
        return "".join(
            self._canonicalize_cluster(cluster) for cluster in split_clusters(text_nfd)
        )

    def _canonicalize_cluster(self, cluster: str) -> str:
        """Reorders combining marks for a single grapheme cluster.

        Args:
            cluster: A single grapheme cluster string.

        Returns:
            The canonicalized cluster string using direct lookup or mark-rank sorting.
        """
        key = to_cluster_key(cluster)
        if key is None:
            return cluster

        canonical_cluster = self._cluster_map.get(key)
        if canonical_cluster is not None:
            return canonical_cluster

        base = cluster[0]
        marks = list(cluster[1:])
        _mark_rank = self._mark_rank

        marks.sort(key=lambda mark: (_mark_rank.get(mark, INF), mark))

        return base + "".join(marks)
