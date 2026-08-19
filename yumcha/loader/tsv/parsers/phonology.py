"""Parser for compiling phonology specifications from raw TSV header and data rows."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from ....core.models.specs import PhonologyData
from ....core.primitives.pattern_tuple import PatternTuple
from ...primitives.directives import PhonologyRowDirective
from ...utils.text import parse_data_cell

if TYPE_CHECKING:
    from ....core.primitives.directives import PhonologyDirectiveMap


def parse(
    id: str,
    headers: list[str],
    data: list[list[str]],
) -> PhonologyData:
    """Parses raw TSV header and data rows into a structured `ParsedContext`.

    Args:
        id: The identifer of the language.
        headers: Header row containing directive column and field names.
        data: Collection of data rows.

    Returns:
        A `PhonologyData` dataclass populated with fields, charsets, directives,
        and invalid patterns.
    """
    intermediate_fields = _parse_headers(headers=headers)
    (
        charsets,
        charset_dicts,
        invalid_pattern_tuples,
    ) = _parse_data(data=data, expected_columns_len=len(headers))

    return PhonologyData(
        id=id,
        fields=intermediate_fields,
        charsets=tuple(charsets),
        char_directives=tuple(charset_dicts),
        invalid_pattern_tuples=tuple(invalid_pattern_tuples),
    )


def _parse_headers(
    headers: list[str],
) -> tuple[str, ...]:
    """Extracts and validates intermediate feature field names from TSV headers.

    The first column header (directive column) is ignored. Remaining headers are cleaned
    and verified to ensure there are no empty field names or duplicate headers.

    Args:
        headers: List of raw header strings from the input table.

    Returns:
        A tuple of cleaned field name strings.

    Raises:
        ValueError: If any field name is empty or if duplicate field names are present.
    """
    intermediate_fields = tuple(s.strip() for s in headers[1:])
    intermediate_fields_dict = {s: idx for idx, s in enumerate(intermediate_fields)}

    if "" in intermediate_fields_dict:
        raise ValueError("intermediate fields cannot be empty")

    if len(intermediate_fields) != len(intermediate_fields_dict):
        counts = Counter(intermediate_fields)
        duplicates = [field for field, count in counts.items() if count > 1]
        raise ValueError(f"duplicated intermediate fields {duplicates}")

    return intermediate_fields


def _parse_data(
    data: list[list[str]],
    expected_columns_len: int,
) -> tuple[
    list[set[str]],  # charsets
    list[PhonologyDirectiveMap],  # charset_dicts
    list[PatternTuple],  # invalid_pattern_tuples
]:
    """Parses phonology table rows into character sets, directives, and invalid patterns.

    Args:
        data: List of raw TSV data rows (excluding headers).
        expected_columns_len: Total number of expected columns per row.

    Returns:
        A tuple containing:
            - `charsets`: List of character sets for each field position.
            - `charset_dicts`: List of maps from character to `PhonologyRowDirective` per field.
            - `invalid_pattern_tuples`: List of pattern tuples denoting invalid combinations.

    Raises:
        ValueError: If a row has an unexpected column count, or if a non-comment/non-invalid
            row contains no concrete character value.
    """
    pattern_tuple_len = expected_columns_len - 1
    charsets: list[set[str]] = [set() for _ in range(pattern_tuple_len)]
    phonology_directive_maps: list[PhonologyDirectiveMap] = [
        {} for _ in range(pattern_tuple_len)
    ]
    invalid_pattern_tuples: list[PatternTuple] = []

    for line_no, row in enumerate(data, start=2):
        if len(row) != expected_columns_len:
            raise ValueError(
                f"malformed data at line {line_no}: "
                + f"expecting columns length of {expected_columns_len}, got {len(row)}"
            )

        row_directive = PhonologyRowDirective(row[0].strip())

        if row_directive is PhonologyRowDirective.COMMENT:
            continue

        parsed_cells = (
            (idx, parsed_cell)
            for idx, cell in enumerate(row[1:])
            if (parsed_cell := cell.strip()) != "..."
        )

        if row_directive is PhonologyRowDirective.INVALID:
            invalid_pattern_tuple = PatternTuple(map(parse_data_cell, row[1:]))
            invalid_pattern_tuples.append(invalid_pattern_tuple)
        else:
            row_intermediate = next(parsed_cells, None)

            if row_intermediate is None:
                raise ValueError(
                    f"invalid data at line {line_no}: expecting one non-ellipsis string"
                )

            row_field_idx, row_char = row_intermediate
            charsets[row_field_idx].add(row_char)
            phonology_directive_maps[row_field_idx][row_char] = (
                row_directive.to_core_directive()
            )

    return charsets, phonology_directive_maps, invalid_pattern_tuples
