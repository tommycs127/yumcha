# ⚙️ How it works

> [!NOTE]
> This document describes the current codebase and may still evolve as the project grows.

Yumcha is built around one idea: represent syllables as structured feature tuples first, then convert between writing systems through that shared structure.

Instead of treating transliteration as string replacement, Yumcha works in three layers:

1. **Phonology** — the language’s intermediate feature space and its constraints.
2. **Scheme definitions** — how a writing system maps onto that shared feature space.
3. **Conversion and validation** — parsing, matching, merging, and roundtrip checking.

The current implementation is centered on the `Language` class, which bundles a phonology with any number of registered schemes. Each scheme can be converted to the language’s intermediate representation, and the intermediate representation can then be converted into any other registered scheme.

## 1. Core data model

### Representation

The basic unit in Yumcha is a `Representation` dataclass.

A `Representation` is an immutable tuple-like object whose fields are stored in definition order. Its string form is the NFC-normalized concatenation of those fields, and iterating over it yields each field value in order.

This makes it usable both as a structured object and as a printable string.

### Phonology

A `Phonology` describes the intermediate sound system of a language.

It stores:

- an identifier
- the `Representation` subclass used for intermediate forms
- ordered field names
- valid character sets per field
- row directives for those character sets
- invalid patterns
- a regex parser for turning text into the representation class

The phonology is loaded from a TSV file, and the class used for the intermediate representation is generated dynamically from the TSV field names.

### Scheme

A `Scheme` describes one surface transcription system.

Like phonology, it has:

- an identifier
- a dynamically generated `Representation` subclass
- ordered intermediate fields
- ordered scheme fields
- an indexer for matching parsed input to pattern rules
- a regex parser
- row directives describing whether each rule is bidirectional, forward-only, or reverse-only

A scheme contains enough information to:

- parse written text into a structured form
- map that structured form into intermediate features
- map intermediate features back into the scheme

## 2. Loading a language

The top-level helper is `yumcha.load_language()`.

It loads a language directory, reads the phonology TSV, then loads every scheme TSV in the scheme folder.

By default, it looks under the bundled `yumcha/languages/` resources. It can also load from a filesystem path or any `Traversable` resource.

If a scheme does not match the phonology requirements, loading fails early.

That validation step is important: the project does not allow an arbitrary scheme to be attached to an arbitrary language.

## 3. Parsing text

A `Language` exposes two parsing entry points:

- `parse_as_intermediate(text)`
- `parse_as_scheme(scheme_id, text)`

Each one uses the relevant regex parser to split input text into the field structure defined by the matching `Representation` class.

This is where written text becomes a structured object that the engine can reason about.

For example, a scheme syllable may be parsed into parts such as:

- initial
- nucleus
- coda
- tone

The actual component names depend on the scheme definition.

## 4. Matching and conversion

### From scheme to intermediate

When converting from a scheme to intermediate form, Yumcha does not simply substitute one symbol for another.

Instead, it:

1. tokenizes the source text into a parsed representation
2. turns that into a `PatternTuple`
3. searches the scheme’s index for the best matching rule set
4. merges compatible rules into a full intermediate tuple
5. optionally validates the result

### From intermediate to scheme

Conversion in the other direction follows the same general flow, but uses the scheme’s forward mapping rules.

The matcher can work with:

- exact strings
- existing `Representation` objects
- iterables of field values

### Scheme to scheme

`scheme_to_scheme()` is implemented as a two-step conversion:

1. source scheme → intermediate
2. intermediate → target scheme

This keeps the conversion logic centralised in the phonology layer instead of forcing every scheme pair to have its own manual bridge.

### Strict and non-strict conversion

The conversion methods support a `strict` flag.

- `strict=True` raises an error when conversion fails.
- `strict=False` returns `None` instead.

That allows the caller to choose between fail-fast behaviour and softer probing.

### Validation

The `validate()` method checks whether a given input can be converted cleanly under the current language and scheme rules.

It runs the same conversion machinery, but treats failure as a validation problem rather than a simple lookup problem.

## 5. How rule matching works

The engine uses a bitmask-based indexer for fast rule lookup.

Each row in a scheme TSV becomes an indexed pattern tuple. The indexer stores those tuples in a way that makes it possible to find matching candidates quickly with bitwise operations rather than repeated linear scans.

When a pattern tuple is queried:

- all compatible candidates are found
- the best matches are merged
- conflicts are rejected
- ambiguous matches raise explicit errors

This is the part of the engine that makes context-sensitive mappings practical.

Some mappings are not one-to-one. A single field value may depend on neighbouring components or on special-case orthographic rules. The indexer and merger are designed to keep those rules expressive without turning the system into a giant handwritten table.

## 6. Validation logic

Validation is handled in `yumcha.validator`.

The validation path checks two things:

1. **Phonotactics** — whether the tuple violates invalid phonological combinations.
2. **Roundtrip stability** — whether converting the result back and forth preserves the expected match set.

If a rule combination is phonologically impossible, validation fails.

If a mapping is unstable or ambiguous in a way that cannot be resolved cleanly, validation also fails.

This is why schemes can be loaded safely: their internal mappings are checked against the language’s phonology, not just against syntax.

## 7. Syllable table generation

`Language.syllable_table()` returns a `SyllableTable` iterator.

The table iterates over every possible phonological combination in the language’s intermediate space and tries to convert each one into every registered scheme.

Rows that cannot be represented in a given scheme are left blank for that scheme column.

The top-level helper `yumcha.write_syllable_table()` writes that table to a TSV file.

It also appends summary rows at the bottom:

- the total number of intermediate combinations
- the number of rows that each scheme can represent
- coverage percentages per scheme

This makes it useful both as a debugging tool and as a way to inspect scheme coverage.

## 8. Loading and writing helpers

Two helper functions are exposed at package level:

- `load_language(language, directory=None, phonology_file_name="phonology.tsv", schemes_folder_name="schemes")`
- `write_syllable_table(language, output_path, progress_bar=None)`

The first one builds a `Language` instance from TSV resources.

The second one exports the full syllable table for a loaded language.

## 9. Design summary

In practical terms, Yumcha behaves like this:

- load a language from TSV resources
- parse text into structured representations
- match each structured input against indexed scheme rules
- convert through the intermediate phonology
- validate the result against phonological and roundtrip constraints
- optionally export the full syllable space as TSV

That gives the project a single conversion core that can support multiple Cantonese and non-Cantonese transcription systems without having to hard-code pairwise conversion tables everywhere.

## 10. Why this structure matters

The reason for the intermediate layer is simplicity of maintenance.

If every scheme had to directly map to every other scheme, the number of pairwise conversion tables would grow quickly and edge cases would become unmanageable. By routing everything through the intermediate representation, the project keeps the logic local to each scheme and the language’s phonology.

That also makes the system easier to extend:

- add a phonology
- define its intermediate representation
- add scheme TSVs that map to it
- let the engine reuse the same conversion machinery

That is the current architectural direction of the project.
