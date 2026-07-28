# 📝 Adding a Language and Custom Schemes

This guide explains how to add a language folder to Yumcha, define its phonology, and set up custom transcription schemes.

Yumcha is file-driven. Each language requires a folder containing a `phonology.tsv` file and a `schemes/` directory containing one or more scheme TSV files. When loaded, Yumcha parses these files, builds internal representations, validates them against each other, and registers a `Language` object.

The fastest way to start is to copy an existing folder from `yumcha/languages/` and modify it.

## 1. Directory Structure

A standard language folder follows this layout:

```text
yumcha/
  languages/
    cantonese/
      phonology.tsv
      schemes/
        braille.tsv
        jyutping.tsv
        yale.tsv
        sidneylau.tsv
```

Custom languages use the exact same structure:

```text
my_languages/
  my_language/
    phonology.tsv
    schemes/
      my_scheme.tsv
      another_scheme.tsv
```

When you call `yumcha.load_language("my_language", directory="/path/to/my_languages")`, Yumcha expects:

- `/path/to/my_languages/my_language/phonology.tsv`
- `/path/to/my_languages/my_language/schemes/*.tsv`

Every `.tsv` file inside `schemes/` will be loaded automatically.

## 2. Naming Conventions

Language directory names and scheme file names **must be valid Python identifiers**.

- **Valid:** `my_language`, `scheme1`, `jyutping`, `slwong_roman`
- **Invalid:** `my-language`, `scheme-1`, `jyutping.tsv.backup`

Yumcha uses the directory name as the language ID and the TSV file name as the scheme ID. Invalid Python identifiers will cause loading errors.

## 3. Writing `phonology.tsv`

The `phonology.tsv` file defines the internal sound system (the intermediate representation) for the language. It specifies:

- Field names (e.g., initial, nucleus, coda, tone)
- Valid values for each field
- Valid, optional, or prohibited combinations

### Header and Directives

The first row is the header. The first cell (directive column) is left blank. Subsequent cells define intermediate field names.

```tsv
	initial	nucleus	coda	tone
```

Every data row starts with a directive character in column 1:

| Directive | Meaning             |
| --------- | ------------------- |
| `*`       | Valid value/feature |
| `?`       | Optional value      |
| `x`       | Invalid combination |
| `#`       | Comment (ignored)   |

Use `...` in a cell to leave that field unconstrained.

### Example Rows (Cantonese)

```tsv
* 	p	...	...	...
* 	pʰ	...	...	...
* 	m	...	...	...
* 	...	aː	...	...
* 	...	...	...	˥
* 	...	...	...	˧˥
* 	...	...	...	˧
```

### Constraint Rules

Every non-comment (`#`) and non-invalid (`x`) row in `phonology.tsv` **must contain exactly one concrete value**. Yumcha uses single-value rows to map values to their corresponding field position. Define phonologies using one-slot rows for each initial, nucleus, coda, and tone.

## 4. Writing `schemes/*.tsv`

A scheme file maps a surface transcription system to the intermediate phonology fields.

### Scheme Header Layout

The header row in a scheme file is split into two parts:

1. **Intermediate Fields** (matches the names in `phonology.tsv`)
2. **Scheme Fields** (written as `scheme_field=intermediate_source`)

```tsv
	initial	nucleus	coda	tone	initial=initial	rime=nucleus,coda	tone=tone
```

The left side of the `=` defines the scheme's field name. The right side defines which intermediate field(s) feed into it.

#### Header Rules and Validation

- Column 1 must be left blank (reserved for directives).
- Intermediate field names must appear first, exactly as defined in `phonology.tsv`.
- Every intermediate field must be referenced by at least one scheme definition.
- Scheme definitions use the format `field_name=source1,source2`.
- Multiple intermediate fields can map to a single scheme field (e.g., `rime=nucleus,coda`).
- A single intermediate field can map across multiple scheme fields (e.g., separating base vowels from diacritics).
- Duplicate field names are not allowed.

## 5. Scheme Header Examples

### Example 1: `braille.tsv` (Combining Fields)

```tsv
	initial	nucleus	coda	tone	initial=initial	rime=nucleus,coda	tone=tone
```

Here, `rime` merges `nucleus` and `coda` into a single surface representation.

### Example 2: `yale.tsv` (Splitting Fields)

```tsv
	initial	nucleus	coda	tone	initial=initial	nucleus_before_tone_diacritic=nucleus	tone_diacritic=tone	nucleus_after_tone_diacritic=nucleus	coda_vowel=coda	tone_h=tone	coda_consonant=coda
```

Yale romanization requires split fields because tone markers and vowels interact positionally. Intermediate fields like `nucleus` and `tone` are referenced multiple times to handle diacritics, trailing letters, and split vowels.

## 6. Scheme Data Rows

Each row after the header contains a directive in column 1, followed by intermediate values and surface mapping values. The total number of columns in each row must match the header exactly.

```tsv
= 	p	...	...	...	b	...	...	...	...	...	...
=	...	aː	...	...	...	a	...	a	...	...	...
=	...	aː	""	...	...	a	...	""	""	...	""
```

> [!TIP]
> **Handling Empty Strings and Quotes in TSV Files**
>
> - **Empty Strings (`""` vs. blank):** While Python's `csv` parser treats blank cells as empty strings, **using explicit `""` is recommended** to avoid confusion.
> - **Literal Double Quotes (`"`):** TSV fields follow standard CSV escaping rules. Any field containing double quotes must be wrapped in `"` quotes, and each inner `"` must be doubled:
>   - For a single literal quote (`"`): Write `""""` (4 quotes).
>   - For two literal quotes (`""`): Write `""""""` (6 quotes).
> - **Literal Single Quotes (`'`):** Single quotes do not act as string delimiters in TSV files and do not need escaping. Simply write `'` in the cell.

### Field Matching Rules

- **`...` (Wildcard):** Leaves the field unconstrained. Yumcha matches and merges partially constrained rows at runtime.
- **`""` (Empty String):** Explicitly matches or outputs an empty string.

### Directives

| Directive | Meaning                                              |
| --------- | ---------------------------------------------------- |
| `=`       | Bidirectional mapping (default for reversible rules) |
| `>`       | Forward-only (mapping from intermediate to scheme)   |
| `<`       | Reverse-only (mapping from scheme to intermediate)   |
| `#`       | Comment (ignored by the parser)                      |

## 7. Minimal Custom Language Example

### `phonology.tsv`

```tsv
	initial	nucleus	tone
* 	p	...	...
* 	m	...	...
* 	...	a	...
* 	...	i	...
* 	...	...	˥
* 	...	...	˩
```

### `schemes/simplelatin.tsv`

```tsv
	initial	nucleus	tone	initial=initial	nucleus=nucleus	tone=tone
= 	p	...	...	p	...	...
= 	m	...	...	m	...	...
= 	...	a	...	...	a	...
= 	...	i	...	...	i	...
= 	...	...	˥	...	...	H
= 	...	...	˩	...	...	L
```

## 8. Python Usage

### Loading a Language

```python
import yumcha

lang = yumcha.load_language(
    "my_language",
    directory="/path/to/my_languages",
)

# List registered schemes
print(list(lang.schemes))
```

### Conversion and Parsing

```python
# Parse a surface string into internal structures or convert between schemes
parsed = lang.parse_as_scheme("simplelatin", "paH")
intermediate = lang.to_intermediate("simplelatin", "paH")
converted = lang.to_scheme("another_scheme", intermediate)
```

### Exporting Syllable Tables

To verify coverage and inspect all generated combinations across your schemes, export a table:

```python
yumcha.write_syllable_table(lang, "/path/to/my_syllable_table.tsv")
```

This outputs a TSV containing every valid intermediate combination, its mapped value in each scheme, and overall coverage metrics.

## 9. Troubleshooting Common Errors

If `load_language()` fails, verify the following:

1. **Pathing:** Ensure `phonology.tsv` and the `schemes/` directory exist in the specified folder.
2. **Identifiers:** Verify directory and scheme file names use underscores rather than hyphens.
3. **Column Counts:** Ensure every data row has the exact same number of tab-separated columns as the header.
4. **Header Syntax:** Check that scheme header definitions match `scheme_field=source1,source2` and that all intermediate fields defined in `phonology.tsv` are mapped.
5. **Single-slot Rule:** Confirm that data rows in `phonology.tsv` contain only **one concrete value** per row.
