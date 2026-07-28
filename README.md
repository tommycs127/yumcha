# 🍵 Yumcha

[![status](https://badgen.net/badge/status/Alpha%20development/red)](#)
[![Python](https://badgen.net/badge/python/3.12%2B)](https://www.python.org/downloads/release/python-3120/)
[![License](https://badgen.net/badge/license/MIT/orange)](LICENSE)
[![type](https://badgen.net/badge/type/Transliteration%20engine/cyan)](#)
[![made-in](https://badgen.net/badge/made%20in/Hong%20Kong/cc3399)](#)

A phonology-oriented transliteration engine for Cantonese and other languages.

> "Yumcha" is a play on Cantonese words. While it traditionally means "drinking tea" (<ruby>飲<rt>jam2</rt>茶<rt>caa4</rt>), it also sounds like a "phonological lookup" (<ruby>音<rt>jam1</rt>查<rt>caa4</rt>).
> Just as tea brings people together, this engine aims to bridge different transcription and phonetic schemes!

> [!CAUTION]
> This project is in its **early stages** and undergoing active development. The API and functionality are **highly unstable** and subject to breaking changes without notice. **Do not use this in production environments.**

## ✨ Highlights

- [**Scheme-to-Scheme Conversion**](#conversion): Convert seamlessly between different transcription and phonetic schemes within the same language.
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
import yumcha

# Bundled in the package
cantonese = yumcha.load_language("cantonese")

# From a directory folder path
colang = yumcha.load_language("/path/to/colang/")
```

The `yumcha.load_language()` method traverses the provided resource directory, parses internal TSV files as phonology rules or schemes, and compiles them into a `Language` instance.

#### Adding custom schemes

> [!NOTE]
> Custom schemes must conform to the language's underlying phonology; otherwise, `yumcha` will raise an exception during initialization. Consult the `Language.phonology` object for required phonemes and constraints.

Use `Language.add_scheme()` method to add custom schemes:

```python
cantonese.add_scheme("/path/to/new_scheme.tsv")
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
parsed = cantonese.parse_as_scheme(
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

Parse an intermediate representation (usually IPA) into components:

```python
parsed = cantonese.parse_as_intermediate(
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

> [!NOTE]
> Converting methods **do not return a `str` object**, but an instance of a `Representation` subclass. To get a string, simply wrap the object in `str()`.

Convert a Jyutping syllable to ILE:

```python
converted = cantonese.scheme_to_scheme(
    from_scheme_id="jyutping",
    to_scheme_id="ile",
    source="seot1",
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

### Getting a full syllable table

> [!NOTE]
> Generating and validating the full dataset may take anywhere from a few seconds to a minute depending on your hardware and the number of active schemes.

Write the full syllable table in TSV format:

```python
yumcha.write_syllable_table(
    language=cantonese,
    output_path="cantonese_syllables.tsv",
)
```

The exported TSV contains a standard header row and two summary rows at the bottom displaying overall syllable counts and scheme coverage percentages.

#### Tracking progress

> [!NOTE]
> Only compatible with progress bar wrappers (such as [`tqdm`](https://tqdm.github.io/) or [`rich.progress`](https://rich.readthedocs.io/en/latest/progress.html)) that accept a `total` keyword argument.

Pass a progress wrapper to the `progress_bar` argument to track generation progress:

```python
from tqdm import tqdm

yumcha.write_syllable_table(
    language=cantonese,
    output_path="cantonese_syllables.tsv",
    progress_bar=tqdm,
)
```

## 🔤 Supported schemes

> [!NOTE]
> While supported schemes strive to remain faithful to their original designs, some syllables may present edge-case constraints.
>
> You can review the pre-generated syllable tables in [this directory](https://github.com/tommycs127/yumcha/tree/main/syllable_tables). These tables are produced by the `yumcha.write_syllable_table()` method.
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

### Documentations

- [x] README.md
- [x] How it works documentation
- [x] Tutorial on adding custom languages and schemes

### Features & Core Engine

- [x] Loading languages and schemes from TSV files
- [x] Scheme parsing and bidirectional conversion
- [x] Syllable table generation and scheme coverage statistics

### Schemes

#### Cantonese

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/14?&label=14/17&min=0&max=17)

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

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/0?&label=0/7&min=0&max=7)

- [ ] Bopomofo (Zhuyin)
- [ ] Gwoyeu Romatzyh
- [ ] Hanyu Pinyin
- [ ] Palladius (Cyrillization)
- [ ] Tongyong Pinyin
- [ ] Wade–Giles
- [ ] Yale

#### Hokkien

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/0?&label=0/4&min=0&max=4)

- [ ] Pe̍h-ōe-jī
- [ ] Phofsit Daibuun
- [ ] Taiwanese Language Phonetic Alphabet
- [ ] Tâi-lô

## 🙏 Acknowledgments

This project implements transcription and phonetic standards developed by linguists and language communities, whose foundational work made this project possible.

## 📜 License

Yumcha is licensed under the [MIT License](LICENSE).
