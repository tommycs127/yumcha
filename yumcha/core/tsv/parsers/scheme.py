import re
from collections import Counter
from dataclasses import dataclass
from types import EllipsisType

from ...models import Pattern, PrePatternTuple, SchemeRowDirective

ID_PATTERN = r"[^\d\W]\w*"
SCHEME_COLUMN_PATTERN = (
    rf"^\s*{ID_PATTERN}\s*=\s*{ID_PATTERN}\s*(,\s*{ID_PATTERN}\s*)*$"
)
SCHEME_COLUMN_RE = re.compile(SCHEME_COLUMN_PATTERN)


@dataclass(frozen=True)
class ParsedContext:
    intermediate_fields: tuple[str, ...]
    scheme_fields: dict[str, frozenset[int]]
    directions: tuple[SchemeRowDirective, ...]
    intermediate_tuples: tuple[PrePatternTuple, ...]
    scheme_tuples: tuple[PrePatternTuple, ...]


def parse_headers(
    headers: list[str],
    headers_split_index: int,
) -> tuple[
    tuple[str, ...],  # intermediate_fields
    dict[str, frozenset[int]],  # scheme_fields
]:
    # Parse intermediate fields

    intermediate_fields = tuple(s.strip() for s in headers[1:headers_split_index])
    intermediate_fields_dict = {s: idx for idx, s in enumerate(intermediate_fields)}

    if "" in intermediate_fields_dict:
        raise ValueError("intermediate fields cannot be empty")

    if len(intermediate_fields) != len(intermediate_fields_dict):
        counts = Counter(intermediate_fields)
        duplicates = [field for field, count in counts.items() if count > 1]
        raise ValueError(f"duplicated intermediate fields {duplicates}")

    # Parse scheme fields

    scheme_cells = headers[headers_split_index:]
    parsed_scheme_fields: dict[str, frozenset[int]] = {}
    seen_scheme_fields = set()
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
                    f"used for scheme field {field!r}"
                )

            unused_intermediate_fields_set.discard(source)
            parsed_sources_mapping.append(intermediate_fields_dict[source])

        parsed_scheme_fields[field] = frozenset(parsed_sources_mapping)

    if unused_intermediate_fields_set:
        raise ValueError(f"unused intermediate fields {unused_intermediate_fields_set}")

    return (
        intermediate_fields,
        parsed_scheme_fields,
    )


def parse_data_cell(s: str) -> Pattern:
    stripped = s.strip()
    return ... if stripped == "..." else stripped


def validate_mapping(
    row_intermediate: PrePatternTuple,
    row_scheme: PrePatternTuple,
    scheme_fields: dict[str, frozenset[int]],
) -> None:
    active_indices: set[int] = {
        idx
        for scheme_pattern, mapping in zip(row_scheme, scheme_fields.values())
        if isinstance(scheme_pattern, str)
        for idx in mapping
    }

    for idx, intermediate_pattern in enumerate(row_intermediate):
        expected_type = str if idx in active_indices else EllipsisType

        if not isinstance(intermediate_pattern, expected_type):
            got_type = type(intermediate_pattern).__name__
            exp_name = expected_type.__name__
            raise TypeError(
                f"index {idx} of intermediate tuple {row_intermediate}: "
                f"expecting {exp_name}, got {got_type}"
            )


def parse_data(
    data: list[list[str]],
    headers_split_index: int,
    expected_columns_len: int,
    scheme_fields: dict[str, frozenset[int]],
) -> tuple[
    tuple[SchemeRowDirective, ...],  # parsed_directions
    tuple[PrePatternTuple, ...],  # parsed_intermediate_tuples
    tuple[PrePatternTuple, ...],  # parsed_scheme_tuples
]:
    parsed_directions: list[SchemeRowDirective] = []
    parsed_intermediate_tuples: list[PrePatternTuple] = []
    parsed_scheme_tuples: list[PrePatternTuple] = []

    seen_intermediate_tuples = set()
    seen_scheme_tuples = set()

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
                f"expecting columns length of {expected_columns_len}, got {len(row)}"
            )

        row_directive = SchemeRowDirective(row[0].strip())

        if row_directive is SchemeRowDirective.COMMENT:
            continue

        row_intermediate = tuple(map(parse_data_cell, row[1:headers_split_index]))
        row_scheme = tuple(map(parse_data_cell, row[headers_split_index:]))

        try:
            validate_mapping(row_intermediate, row_scheme, scheme_fields)
        except TypeError as te:
            raise TypeError(f"malformed data at line {line_no}: {te}") from te

        if row_directive in CHECK_INTERMEDIATE:
            if row_intermediate in seen_intermediate_tuples:
                raise ValueError(
                    f"conflict at line {line_no}: "
                    f"duplicated intermediate tuple {row_intermediate}"
                )
            seen_intermediate_tuples.add(row_intermediate)

        if row_directive in CHECK_SCHEME:
            if row_scheme in seen_scheme_tuples:
                raise ValueError(
                    f"conflict at line {line_no}: duplicated scheme tuple {row_scheme}"
                )
            seen_scheme_tuples.add(row_scheme)

        parsed_directions.append(row_directive)
        parsed_intermediate_tuples.append(row_intermediate)
        parsed_scheme_tuples.append(row_scheme)

    return (
        tuple(parsed_directions),
        tuple(parsed_intermediate_tuples),
        tuple(parsed_scheme_tuples),
    )


def get_headers_split_index(headers: list[str]) -> int:
    return next(
        (i for i, s in enumerate(headers) if SCHEME_COLUMN_RE.fullmatch(s.strip())),
        len(headers),
    )


def parse(
    headers: list[str],
    data: list[list[str]],
) -> ParsedContext:
    headers_split_index = get_headers_split_index(headers)

    if headers_split_index < 2:
        raise ValueError(
            "invalid header layout: "
            "must have at least two header cells before scheme definitions begin"
        )
    if headers_split_index == len(headers):
        raise ValueError(
            "invalid header layout: at least one scheme field must be present "
            "(e.g. 'initial=initial' at the first column of scheme headers)"
        )

    (
        intermediate_fields,
        scheme_fields,
    ) = parse_headers(headers, headers_split_index)

    (
        directions,
        intermediate_tuples,
        scheme_tuples,
    ) = parse_data(data, headers_split_index, len(headers), scheme_fields)

    return ParsedContext(
        intermediate_fields,
        scheme_fields,
        directions,
        intermediate_tuples,
        scheme_tuples,
    )
