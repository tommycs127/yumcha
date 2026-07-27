import re
import unicodedata


class Regexer:
    regex_pattern: re.Pattern[str]

    def __init__(self, charsets: list[set[str]]):
        self._canonical_cluster_map: dict[tuple[str, tuple[str, ...]], str] = {}
        self._mark_rank: dict[str, int] = {}

        nfd_charsets: list[set[str]] = [
            {unicodedata.normalize("NFD", char) for char in charset}
            for charset in charsets
        ]

        self._learn_canonical_clusters(nfd_charsets)

        regex_parts = []
        for charset in nfd_charsets:
            normalized_charset = {self._canonicalize_text_from_nfd(c) for c in charset}
            sorted_chars = sorted(
                normalized_charset,
                key=lambda c: (len(c), c),
                reverse=True,
            )
            escaped_chars = [re.escape(c) for c in sorted_chars]
            alternation_pattern = "|".join(escaped_chars)
            regex_parts.append(f"({alternation_pattern})")

        self.regex_pattern = re.compile("".join(regex_parts))

    def tokenize(self, text: str) -> tuple[str, ...]:
        text_norm = self._canonicalize_text(text)
        matched = self.regex_pattern.fullmatch(text_norm)

        if not matched:
            raise ValueError(f"invalid text {text!r}")

        return matched.groups()

    def _canonicalize_text(self, text: str) -> str:
        text_nfd = unicodedata.normalize("NFD", text)
        return self._canonicalize_text_from_nfd(text_nfd)

    def _canonicalize_text_from_nfd(self, text_nfd: str) -> str:
        return "".join(
            self._canonicalize_cluster(cluster)
            for cluster in self._split_clusters(text_nfd)
        )

    def _canonicalize_cluster(self, cluster: str) -> str:
        """Canonicalize one base+marks cluster.

        Strategy:
        1) If this exact base + mark set is known from the scheme,
           use the learned canonical spelling.
        2) Otherwise, apply a deterministic fallback ordering by learned mark rank.
        """
        key = self._cluster_key(cluster)
        if key is None:  # empty or stray combining cluster
            return cluster

        canonical = self._canonical_cluster_map.get(key)
        if canonical is not None:
            return canonical

        # Fall back to a deterministic ordering if cluster shape is unknown for this scheme
        base = cluster[0]
        marks = list(cluster[1:])

        marks.sort(key=lambda m: (self._mark_rank.get(m, float("inf")), m))
        return base + "".join(marks)

    def _learn_canonical_clusters(self, nfd_charsets: list[set[str]]) -> None:
        seen_sources: dict[tuple[str, tuple[str, ...]], str] = {}

        for charset in nfd_charsets:
            for token in charset:
                for cluster in self._split_clusters(token):
                    key = self._cluster_key(cluster)
                    if key is None:
                        continue

                    old = self._canonical_cluster_map.get(key)
                    if old is None:
                        self._canonical_cluster_map[key] = cluster
                        seen_sources[key] = token
                    elif old != cluster:
                        raise ValueError(
                            "conflicting canonical cluster order for "
                            f"{key}: {old!r} (from {seen_sources[key]!r}) "
                            f"vs {cluster!r} (from {token!r})"
                        )

        # Learn fallback mark rank from the canonical cluster spellings
        for canonical_cluster in self._canonical_cluster_map.values():
            if unicodedata.combining(canonical_cluster[0]) != 0:
                continue

            marks = canonical_cluster[1:]
            for pos, mark in enumerate(marks):
                old_rank = self._mark_rank.get(mark)
                if old_rank is None or pos < old_rank:
                    self._mark_rank[mark] = pos

    def _split_clusters(self, nfd_text: str) -> list[str]:
        clusters = []
        current = ""

        for ch in nfd_text:
            if unicodedata.combining(ch) == 0:
                if current:
                    clusters.append(current)
                current = ch
            else:
                if not current:
                    current = ch
                else:
                    current += ch

        if current:
            clusters.append(current)

        return clusters

    def _cluster_key(self, cluster: str) -> tuple[str, tuple[str, ...]] | None:
        """Return a key that ignores mark order but preserves multiplicity."""
        if not cluster:
            return None

        if unicodedata.combining(cluster[0]) != 0:
            return None

        base = cluster[0]
        marks = tuple(sorted(cluster[1:]))
        return (base, marks)
