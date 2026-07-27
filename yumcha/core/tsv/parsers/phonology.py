from collections import Counter
from dataclasses import dataclass
from types import EllipsisType

from ...models import CharsetDict, PhonologyRowDirective


@dataclass(frozen=True)
class ParsedContext:
    fields: tuple[str, ...]
    charsets: list[set[str]]
    charset_dicts: list[CharsetDict]
    invalid_patterns: list[tuple[str | EllipsisType, ...]]


def parse_headers(
    headers: list[str],
) -> tuple[str, ...]:
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
