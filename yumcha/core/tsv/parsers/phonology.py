from collections import Counter
from dataclasses import dataclass
from types import EllipsisType

from ...models import CharsetDict, PhonologyRowDirective


@dataclass(frozen=True)
class ParsedContext:
    """Container holding parsed phonology table data.

    Attributes:
        fields: Tuple of header field names.
        charsets: List of character sets (one set per field position).
        charset_dicts: List of dictionaries mapping characters to their row directives per field.
        invalid_patterns: List of tuples representing invalid feature pattern wildcards/strings.
    """

    fields: tuple[str, ...]
    charsets: list[set[str]]
    charset_dicts: list[CharsetDict]
    invalid_patterns: list[tuple[str | EllipsisType, ...]]


def parse_headers(
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


def parse_data(
    data: list[list[str]],
    expected_columns_len: int,
) -> tuple[
    list[set[str]],  # charsets
    list[CharsetDict],  # charset_dicts
    list[tuple[str | EllipsisType, ...]],  # invalid_patterns
]:
    """Parses phonology table rows into character sets, directives, and invalid patterns.

    Args:
        data: List of raw TSV data rows (excluding headers).
        expected_columns_len: Total number of expected columns per row.

    Returns:
        A tuple containing:
            - `charsets`: List of character sets for each field position.
            - `charset_dicts`: List of maps from character to `PhonologyRowDirective` per field.
            - `invalid_patterns`: List of pattern tuples denoting invalid combinations.

    Raises:
        ValueError: If a row has an unexpected column count, or if a non-comment/non-invalid
            row contains no concrete character value.
    """
    tuple_len = expected_columns_len - 1
    charsets: list[set[str]] = [set() for _ in range(tuple_len)]
    charset_dicts: list[CharsetDict] = [{} for _ in range(tuple_len)]
    invalid_patterns: list[tuple[str | EllipsisType, ...]] = []

    for line_no, row in enumerate(data, start=2):
        if len(row) != expected_columns_len:
            raise ValueError(
                f"malformed data at line {line_no}: "
                f"expecting columns length of {expected_columns_len}, got {len(row)}"
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
            invalid_patterns.append(tuple(... if p == "..." else p for p in row[1:]))
        else:
            row_intermediate = next(parsed_cells, None)

            if row_intermediate is None:
                raise ValueError(
                    f"invalid data at line {line_no}: expecting one non-ellipsis string"
                )

            row_field_idx, row_char = row_intermediate
            charsets[row_field_idx].add(row_char)
            charset_dicts[row_field_idx][row_char] = row_directive

    return charsets, charset_dicts, invalid_patterns


def parse(
    headers: list[str],
    data: list[list[str]],
) -> ParsedContext:
    """Parses raw TSV header and data rows into a structured `ParsedContext`.

    Args:
        headers: Header row containing directive column and field names.
        data: Collection of data rows.

    Returns:
        A `ParsedContext` dataclass populated with fields, charsets, directives,
        and invalid patterns.
    """
    intermediate_fields = parse_headers(headers=headers)
    (
        charsets,
        charset_dicts,
        invalid_patterns,
    ) = parse_data(data=data, expected_columns_len=len(headers))

    return ParsedContext(
        fields=intermediate_fields,
        charsets=charsets,
        charset_dicts=charset_dicts,
        invalid_patterns=invalid_patterns,
    )
