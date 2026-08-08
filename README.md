# 🍵 Yumcha

[![status](https://img.shields.io/badge/status-Alpha_development-red)](#)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)
[![type](https://img.shields.io/badge/type-Transliteration_engine-cyan)](#)
[![made-in](https://img.shields.io/badge/made_in-Hong_Kong-cc3399)](#)

A phonology-oriented transliteration engine for Cantonese and other languages.

> "Yumcha" is a play on Cantonese words. While it traditionally means "drinking tea" (<ruby>飲<rt>jam2</rt>茶<rt>caa4</rt>), it also sounds like a "phonological lookup" (<ruby>音<rt>jam1</rt>查<rt>caa4</rt>).
> Just as tea brings people together, this engine aims to bridge different transcription and phonetic schemes!

> [!CAUTION]
> This project is in its **early stages** and undergoing active development. The API and functionality are **highly unstable** and subject to breaking changes without notice. Outputs are **not guaranteed to be correct** and manual verification is advised. **Use at your own risk.**

## ✨ Highlights

- [**Scheme-to-Scheme Conversion**](#conversion): Convert a syllable seamlessly between different transcription and phonetic schemes within the same language.
- [**Scheme Parsing**](#parsing): Parse strings to identify their phonological components and their intermediate representations.
- [**Syllable Table Generation**](#getting-a-full-syllable-table): Get all valid syllables of every scheme via the phonology of the language.
- [**Modular & Extensible**](/docs/custom-phonology-and-schemes.md): Add new language by defining its phonology, and add new schemes by simply defining the representation structure and an intermediate-to-symbol map!
- **Zero Third-Party Dependencies:** Lightweight and easy to integrate into any project.
- **Type-hinted**: Built with modern Python 3.12+ type hints for better IDE support and readability.

## 🤔 Why Yumcha?

Sinitic transcription is fragmented and converting between systems often requires large handwritten mapping tables, which break down for edge cases such as unusual spellings and tone markings.

Yumcha provides a unified API to convert these schemes without requiring the user to write complex mapping logic or maintaining large mapping tables that can miss edge cases.

## 📋 Requirements

Python 3.12 or above.

## 📦 Installation

Install Yumcha using `pip`:

```bash
pip install git+https://github.com/tommycs127/yumcha.git
```

## 🚀 Usage

### Initialization

Import `yumcha` and load a language by its bundled name or by providing a path to a custom language directory/package:

```python
from yumcha.loader.tsv import load_language

# Bundled in the package
cantonese = load_language("cantonese")

# From a directory folder path
colang = load_language("colang", directory="/path/to")
```

The `load_language()` method traverses the provided resource directory, parses internal TSV files as phonology rules or schemes, and compiles them into a `Language` instance.

#### Adding custom schemes

> [!NOTE]
> Custom schemes must conform to the language’s underlying phonology; otherwise, Yumcha will raise an exception during initialization. Consult the `Language.phonology` object or its source file for required phonemes and constraints.

Use the `Language.add_scheme()` method to add custom schemes:

```python
from yumcha.loader.tsv import load_scheme_from_tsv

# Load the custom scheme
my_scheme = load_scheme_from_tsv("/path/to/my_scheme.tsv")

# Add the scheme by passing the loaded object
cantonese.add_scheme(my_scheme)
```

### Getting available schemes

```python
print(list(cantonese.schemes))
```

Output:

```python
[
    'braille',
    'hangul',
    'ile',
    ...,
    'slwong_roman',
    'yale',
    'yutyut'
]
```

### Parsing

#### Scheme representation

Parse a Yale syllable into components:

```python
parsed = cantonese.parse_to_scheme(
    scheme_id="yale",
    text="chēun",
)
print(repr(parsed))
```

Output:

```python
Yale(
    initial='ch',
    nucleus_before_tone_diacritic='e',
    tone_diacritic='̄',
    nucleus_after_tone_diacritic='u',
    coda_vowel='',
    tone_h='',
    coda_consonant='n'
)
```

Access individual components directly as attributes:

```python
print(parsed.initial)  # Output: 'ch'
print(parsed.coda_consonant)  # Output: 'n'
```

#### Intermediate representation

Parse an intermediate representation (usually [IPA](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet)) into components:

```python
parsed = cantonese.parse_to_intermediate(
    text="tɪŋ˧˥",
)
print(repr(parsed))
```

Output:

```python
Cantonese(
    initial='t',
    nucleus='ɪ',
    coda='ŋ',
    tone='˧˥'
)
```

### Conversion

#### Scheme to Scheme

> [!NOTE]
> Converting methods **do not return a `str` object**, but an instance of a `Representation` subclass. To get a string, simply wrap the object in `str()`.

Convert a Jyutping syllable to ILE:

```python
converted = cantonese.convert_scheme_to_scheme(
    source="seot1",
    from_scheme_id="jyutping",
    to_scheme_id="ile",
)
print(str(converted))  # Output: 'soet7'
print(repr(converted))
```

Output:

```python
Ile(
    initial='s',
    nucleus='oe',
    coda='t',
    tone='7'
)
```

#### Scheme to Intermediate

Convert a Sidney Lau syllable to intermediate representation:

```python
converted = cantonese.convert_scheme_to_intermediate(
    source="fei1°",
    scheme_id="sidneylau",
)
print(repr(converted))
```

Output:

```python
Cantonese(
    initial='f',
    nucleus='e',
    coda='i̯',
    tone='˥'
)
```

#### Intermediate to Scheme

Convert an intermediate representation to Meyer–Wempe:

```python
converted = cantonese.convert_intermediate_to_scheme(
    source="lɛːm˧˥",
    scheme_id="meyer_wempe",
)
print(repr(converted))
```

Output:

```python
MeyerWempe(
    initial='l',
    nucleus='e',
    coda_vowel='',
    tone='́',
    coda_consonant='m'
)
```

### Getting a full syllable table

> [!NOTE]
> Generating and validating the full dataset may take anywhere from a few seconds to a minute depending on your hardware, active schemes, and exporter settings.
>
> Pass `loader_fn` and `loader_args` to Exporter to enable multi-process parallel generation; omitting them runs the export in single-process mode.

Write the full syllable table in TSV format:

```python
from yumcha.exporter import Exporter
from yumcha.loader.tsv import load_language

language_id = "cantonese"
cantonese = load_language(language_id)

exporter = Exporter(
    cantonese,
    loader_fn=load_language,
    loader_args=(language_id,),  # For non-bundled languages: (language_id, "/path/to/directory")
)
exporter.export("/path/to/cantonese_syllables.tsv")
```

The exported TSV contains a standard header row and two summary rows at the bottom displaying overall syllable counts and scheme coverage percentages.

#### Tracking progress

> [!NOTE]
> Only compatible with progress bar wrappers (such as [`tqdm`](https://tqdm.github.io/) or [`rich.progress`](https://rich.readthedocs.io/en/latest/progress.html)) that accept a `total` keyword argument.

Pass a progress wrapper to the `progress_bar` argument to track generation progress:

```python
from tqdm import tqdm

exporter.export("/path/to/cantonese_syllables.tsv", progress_bar=tqdm)
```

## 🔤 Supported schemes

> [!NOTE]
> While supported scheme files strive to remain faithful to their original designs, some syllables may present edge-case constraints.
>
> You can review the pre-generated syllable tables in [this directory](https://github.com/tommycs127/yumcha/tree/main/syllable_tables). These tables are produced by the [`Exporter.export()`](#getting-a-full-syllable-table) method.
>
> If you spot any discrepancies, please [open an issue](https://github.com/tommycs127/yumcha/issues/new). Any help is welcome and appreciated!

### Cantonese

| Scheme name                                           | Example      | Scheme code       | Note                                                               |
| ----------------------------------------------------- | ------------ | ----------------- | ------------------------------------------------------------------ |
| Braille                                               | `⠭⠎⠀`        | `braille`         |                                                                    |
| Hangul (T. S. Wong Scheme)                            | `츈`         | `hangul`          | Display may vary depending on Unicode combining character support. |
| Institute of Language in Education Scheme             | `tsoen1`     | `ile`             |                                                                    |
| Jyutping                                              | `ceon1`      | `jyutping`        |                                                                    |
| Kuping                                                | `tśeon55^1`  | `kuping`          | A romanization scheme I designed!                                  |
| Kuping (Alternative)                                  | `ts'eon55^1` | `kuping_alt`      | Ditto.                                                             |
| Meyer–Wempe                                           | `ts'un`      | `meyer_wempe`     |                                                                    |
| Pênkyämp                                              | `cönt`       | `penkyamp`        | Glottal stop coda (`q`) is not implemented.                        |
| Cantonese Transliteration Scheme (Rao's Romanization) | `cên1`       | `rao`             |                                                                    |
| Sidney Lau                                            | `chun1°`     | `sidneylau`       | Tone degree symbol is not superscripted.                           |
| S. L. Wong (Romanization)                             | `ˈtseun`     | `slwong_roman`    | Conventional numeral tone marking is not implemented.              |
| S. L. Wong (Phonetic)                                 | `ˈtsœn`      | `slwong_phonetic` | Ditto.                                                             |
| Yale                                                  | `chēun`      | `yale`            |                                                                    |
| Yựtyựt                                                | `cơn`        | `yutyut`          |                                                                    |

## ⚙️ How it works

Please refer to the [How it works](/docs/how-it-works.md) documentation.

## 🚫 Limitations

### No Tone Sandhi

Tone sandhi depends on linguistic context (e.g., phonological environment) and is therefore out of scope for this project.

### Scheme-Specific Limitations

- **Information Loss during Conversion:** Certain schemes track historical phonemes or granular tone contours. For example, the Sidney Lau scheme distinguishes high-flat (`1°`) from high-falling (`1`), whereas Jyutping uses `1` for both. Converting through a less granular scheme may lose tone contour specifics.
- **Unrepresentable Syllables:** Some orthographies cannot represent every phonological combination. For example, S. L. Wong Romanization uses `eu` for `[yː]`, making `[ɛːu̯]` unrepresentable. Converting inputs like `deu6` (Jyutping) to S. L. Wong Romanization will return no valid output.

## 🛣️ Roadmap

### Documentation

- [x] README.md
- [x] How it works documentation
- [x] Tutorial on adding custom languages and schemes

### Features & Core Engine

- [x] Loading languages and schemes from TSV files
- [x] Scheme parsing and bidirectional conversion
- [x] Syllable table generation and scheme coverage statistics

### Schemes

#### Cantonese

![Cantonese Progress](<https://img.shields.io/badge/14%2F17_(82%25)-green>)

- [x] Braille
- [x] Cantonese Hangul (T. S. Wong Scheme)
- [x] Cantonese Transliteration Scheme (Rao's Romanization)
- [x] Institute of Language in Education Scheme
- [x] Jyutping
- [x] Kuping
- [x] Kuping (Alternative)
- [x] Meyer–Wempe
- [x] Pênkyämp
- [x] S. L. Wong (Romanization)
- [x] S. L. Wong (Phonetic)
- [x] Sidney Lau
- [x] Yale
- [x] Yựtyựt
- [ ] Barnett–Chao
- [ ] ~~Bopomofo (Zhuyin) by the Commission on the Unification of Pronunciation~~
  - Will not be implemented until Unicode supports the missing characters.
- [ ] Bopomofo (Zhuyin) by the People's Government Culture and Education Department
- [ ] Standard Romanisation

#### Mandarin

![Mandarin Progress](<https://img.shields.io/badge/0%2F7_(0%25)-red>)

- [ ] Bopomofo (Zhuyin)
- [ ] Gwoyeu Romatzyh
- [ ] Hanyu Pinyin
- [ ] Palladius (Cyrillization)
- [ ] Tongyong Pinyin
- [ ] Wade–Giles
- [ ] Yale

#### Hokkien

![Hokkien Progress](<https://img.shields.io/badge/0%2F4_(0%25)-red>)

- [ ] Pe̍h-ōe-jī
- [ ] Phofsit Daibuun
- [ ] Taiwanese Language Phonetic Alphabet
- [ ] Tâi-lô

## 🙏 Acknowledgments

This project implements transcription and phonetic standards developed by linguists and language communities, whose foundational work made this project possible.

## 📜 License

Yumcha is licensed under the [MIT License](LICENSE).
