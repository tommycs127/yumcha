# Syllable Table Specifications

All the syllable tables are presented in Tab-Separated Values (`.tsv`) format.

- **Column Headers**: Represents the code names of the supported schemes.
- **Row Headers**: Represents the intermediate representation, primarily written in the International Phonetic Alphabet (IPA).

## Legend of Symbols

The following symbols may appear in the tables:

- `△` (Triangle) Indicates that the scheme lacks a corresponding representation for the syllable.
- `⊖` (Circled Minus) Indicates that the representation is invalidated by the constraints defined in the corresponding `Representation` subclass.
- `↦` (Rightwards Arrow from Bar) Indicates that the representation is inaccurate and cannot be mapped back to the intermediate representation (the row header).
  - The syllable in square brackets shows how it will be interpreted instead.
  - **Note:** This redirection may be intentional and does not necessarily indicate an error. Examples include:
    - Normalizing a syllable to its standard pronunciation.
    - Mapping a historical pronunciation to a modern one.

## Totals and Aggregations

- **Row Totals** (The final column of each row): Represents the count of schemes supporting that specific syllable.
- **Column Totals** (The final row of the table): Provides the total count of the syllables supported by each individual scheme.
- **Grand Total** (the bottom-right cell): Represents the total count of all pronounceable syllables of the language.

**Note:** Any representation marked with the symbols listed above is excluded from these counts.
