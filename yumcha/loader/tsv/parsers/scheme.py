"""Parser for compiling orthographic/romanization scheme specifications from raw TSV rows."""

from __future__ import annotations

import re
from collections import Counter
from types import EllipsisType
from typing import TYPE_CHECKING

from ....core.models.specs import SchemeData
from ....core.primitives.pattern_tuple import PatternTuple
from ...primitives.directives import SchemeRowDirective
from ...utils.text import parse_data_cell

if TYPE_CHECKING:
    from ....core.primitives.directives import SchemeDirective
    from ....core.primitives.pattern import Pattern
    from ...primitives.pre_pattern_tuple import PrePatternTuple


ID_PATTERN = r"[^\d\W]\w*"
"""Regex pattern string matching valid Python-style identifier names."""

SCHEME_COLUMN_PATTERN = (
    rf"^\s*{ID_PATTERN}\s*=\s*{ID_PATTERN}\s*(,\s*{ID_PATTERN}\s*)*$"
)
"""Regex pattern string for validating scheme header definitions (e.g., 'scheme=intermediate')."""

SCHEME_COLUMN_RE = re.compile(SCHEME_COLUMN_PATTERN)
"""Compiled regular expression for matching scheme column header syntax."""


def parse(
    scheme_id: str,
    headers: list[str],
    data: list[list[str]],
) -> SchemeData:
    """Parses raw TSV headers and data rows into a structured `ParsedContext`.

    Args:
        headers: Header row cell strings from the TSV file.
        data: Collection of data row cell strings.

    Returns:
        A fully constructed `ParsedContext` dataclass.

    Raises:
        ValueError: If TSV header layout is malformed or missing scheme definitions.
    """
    headers_split_index = _get_headers_split_index(headers)

    if headers_split_index < 2:
        raise ValueError(
            "invalid header layout: "
            + "must have at least two header cells before scheme definitions begin"
        )
    if headers_split_index == len(headers):
        raise ValueError(
            "invalid header layout: at least one scheme field must be present "
            + "(e.g. 'initial=initial' at the first column of scheme headers)"
        )

    (
        intermediate_fields,
        fields,
    ) = _parse_headers(headers, headers_split_index)

    (
        directions,
        intermediate_pattern_tuples,
        pattern_tuples,
        invalid_pattern_tuples,
    ) = _parse_data(data, headers_split_index, len(headers), fields)

    return SchemeData(
        scheme_id,
        directions,
        intermediate_fields,
        intermediate_pattern_tuples,
        fields,
        pattern_tuples,
        invalid_pattern_tuples,
    )


def _parse_headers(
    headers: list[str],
    headers_split_index: int,
) -> tuple[
    dict[str, frozenset[int]],  # intermediate_fields
    dict[str, frozenset[int]],  # scheme_fields
]:
    """Parses TSV table headers into intermediate fields and scheme field mappings.

    Args:
        headers: List of header cell strings from the input TSV file.
        headers_split_index: The column index separating intermediate fields from scheme fields.

    Returns:
        A tuple containing:
            - `intermediate_fields`: Cleaned tuple of intermediate field names.
            - `scheme_fields`: Map of target scheme names to frozensets of source field indices.

    Raises:
        ValueError: If intermediate fields are empty or duplicated, or if scheme syntax/references
            are invalid or leave intermediate fields unmapped.
    """
    intermediate_fields = tuple(s.strip() for s in headers[1:headers_split_index])
    intermediate_fields_dict = {s: idx for idx, s in enumerate(intermediate_fields)}

    if "" in intermediate_fields_dict:
        raise ValueError("intermediate fields cannot be empty")

    if len(intermediate_fields) != len(intermediate_fields_dict):
        counts = Counter(intermediate_fields)
        duplicates = [field for field, count in counts.items() if count > 1]
        raise ValueError(f"duplicated intermediate fields {duplicates}")

    scheme_cells = headers[headers_split_index:]
    parsed_scheme_fields: dict[str, frozenset[int]] = {}
    seen_scheme_fields: set[str] = set()
    unused_intermediate_fields_set = set(intermediate_fields)

    for scheme_cell in scheme_cells:
        if scheme_cell.count("=") != 1:
            raise ValueError("scheme headers must only have one equal sign ('=')")

        field, sources_str = scheme_cell.split("=", 1)
        field = field.strip()

        if not field:
            raise ValueError("empty scheme field")
        if field in seen_scheme_fields:
            raise ValueError(f"duplicated scheme field {field!r}")
        if not sources_str.strip():
            raise ValueError(
                f"scheme field {field!r} must specify at least one intermediate field"
            )

        seen_scheme_fields.add(field)

        parsed_sources_mapping: list[int] = []
        for source in sources_str.split(","):
            source = source.strip()
            if source not in intermediate_fields_dict:
                raise ValueError(
                    f"invalid intermediate field {source!r} "
                    + f"used for scheme field {field!r}"
                )

            unused_intermediate_fields_set.discard(source)
            parsed_sources_mapping.append(intermediate_fields_dict[source])

        parsed_scheme_fields[field] = frozenset(parsed_sources_mapping)

    if unused_intermediate_fields_set:
        raise ValueError(f"unused intermediate fields {unused_intermediate_fields_set}")

    pre_intermediate_fields: dict[str, set[int]] = {
        field: set() for field in intermediate_fields
    }

    for scheme_idx, indexes in enumerate(parsed_scheme_fields.values()):
        for idx in indexes:
            intermediate_field = intermediate_fields[idx]
            pre_intermediate_fields[intermediate_field].add(scheme_idx)

    parsed_intermediate_fields: dict[str, frozenset[int]] = {
        key: frozenset(value) for key, value in pre_intermediate_fields.items()
    }

    return (
        parsed_intermediate_fields,
        parsed_scheme_fields,
    )


def _validate_mapping(
    row_intermediate: PrePatternTuple,
    row_scheme: PrePatternTuple,
    scheme_fields: dict[str, frozenset[int]],
) -> None:
    """Validates structural type consistency between intermediate and scheme tuple values.

    Args:
        row_intermediate: Intermediate pattern tuple for a single row.
        row_scheme: Scheme pattern tuple for a single row.
        scheme_fields: Map of scheme field names to intermediate field index mappings.

    Raises:
        TypeError: If an intermediate slot expected to be active contains an ellipsis,
            or if an inactive slot contains a string value.
    """
    active_indices: set[int] = {
        idx
        for scheme_pattern, mapping in zip(row_scheme, scheme_fields.values())
        if isinstance(scheme_pattern, str)
        for idx in mapping
    }

    for idx, intermediate_pattern in enumerate(row_intermediate):
        expected_type = str if idx in active_indices else EllipsisType

        if type(intermediate_pattern) is not expected_type:
            got_type = type(intermediate_pattern).__name__
            exp_name = expected_type.__name__
            raise TypeError(
                f"index {idx} of intermediate tuple {row_intermediate!r}: "
                + f"expecting {exp_name}, got {got_type}"
            )


def _parse_data(
    data: list[list[str]],
    headers_split_index: int,
    expected_columns_len: int,
    scheme_fields: dict[str, frozenset[int]],
) -> tuple[
    tuple[SchemeDirective, ...],  # parsed_directions
    tuple[PatternTuple, ...],  # parsed_intermediate_pattern_tuples
    tuple[PatternTuple, ...],  # parsed_pattern_tuples
    tuple[PatternTuple, ...],  # parsed_invalid_pattern_tuples
]:
    """Parses TSV data rows into directives and tuple sequences.

    Args:
        data: List of raw TSV row cell lists (excluding headers).
        headers_split_index: Column index where scheme definitions begin.
        expected_columns_len: Total expected columns per row.
        scheme_fields: Field mapping specification from intermediate to scheme slots.

    Returns:
        A tuple containing:
            - `parsed_directions`: Tuple of row directive direction flags.
            - `parsed_intermediate_pattern_tuples`: Parsed intermediate pattern tuples.
            - `parsed_pattern_tuples`: Parsed scheme pattern tuples.
            - `parsed_invalid_pattern_tuples`: Parsed invalid scheme pattern tuples.

    Raises:
        ValueError: If row lengths differ from expectations or if duplicate entries conflict
            with direction rules.
        TypeError: If intermediate and scheme pattern types fail validation pattern tuples.
    """
    parsed_directions: list[SchemeDirective] = []
    parsed_intermediate_pattern_tuples: list[PatternTuple] = []
    parsed_pattern_tuples: list[PatternTuple] = []
    parsed_invalid_pattern_tuples: list[PatternTuple] = []

    seen_intermediate_pattern_tuples: set[tuple[Pattern, ...]] = set()
    seen_pattern_tuples: set[tuple[Pattern, ...]] = set()
    seen_invalid_pattern_tuples: set[tuple[Pattern, ...]] = set()

    CHECK_INTERMEDIATE = {
        SchemeRowDirective.BIDIRECTIONAL,
        SchemeRowDirective.FORWARD,
    }
    CHECK_SCHEME = {
        SchemeRowDirective.BIDIRECTIONAL,
        SchemeRowDirective.REVERSE,
    }

    for line_no, row in enumerate(data, start=2):
        if len(row) != expected_columns_len:
            raise ValueError(
                f"malformed data at line {line_no}: "
                + f"expecting columns length of {expected_columns_len}, got {len(row)}"
            )

        row_directive = SchemeRowDirective(row[0].strip())

        if row_directive is SchemeRowDirective.COMMENT:
            continue

        row_intermediate = tuple(map(parse_data_cell, row[1:headers_split_index]))
        row_scheme = tuple(map(parse_data_cell, row[headers_split_index:]))

        try:
            _validate_mapping(row_intermediate, row_scheme, scheme_fields)
        except TypeError as te:
            raise TypeError(f"malformed data at line {line_no}: {te}") from te

        if row_directive is SchemeRowDirective.INVALID:
            seen_invalid_pattern_tuples.add(row_scheme)
            parsed_invalid_pattern_tuples.append(PatternTuple(row_scheme))
            continue

        if row_directive in CHECK_INTERMEDIATE:
            if row_intermediate in seen_intermediate_pattern_tuples:
                raise ValueError(
                    f"conflict at line {line_no}: "
                    + f"duplicated intermediate tuple {row_intermediate!r}"
                )
            seen_intermediate_pattern_tuples.add(row_intermediate)

        if row_directive in CHECK_SCHEME:
            if row_scheme in seen_pattern_tuples:
                raise ValueError(
                    f"conflict at line {line_no}: duplicated scheme tuple {row_scheme!r}"
                )
            seen_pattern_tuples.add(row_scheme)

        parsed_directions.append(row_directive.to_core_directive())
        parsed_intermediate_pattern_tuples.append(PatternTuple(row_intermediate))
        parsed_pattern_tuples.append(PatternTuple(row_scheme))

    return (
        tuple(parsed_directions),
        tuple(parsed_intermediate_pattern_tuples),
        tuple(parsed_pattern_tuples),
        tuple(parsed_invalid_pattern_tuples),
    )


def _get_headers_split_index(headers: list[str]) -> int:
    """Finds the column index in header row where scheme field definitions begin.

    Args:
        headers: List of header cell strings.

    Returns:
        The 0-based column index of the first scheme definition header, or `len(headers)`
        if no scheme definitions were found.
    """
    return next(
        (i for i, s in enumerate(headers) if SCHEME_COLUMN_RE.fullmatch(s.strip())),
        len(headers),
    )
