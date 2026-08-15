# 🍵 Yumcha

[![status](https://img.shields.io/badge/status-Alpha_development-red)](#)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/release/python-3120/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)
[![type](https://img.shields.io/badge/type-Transliteration_engine-cyan)](#)
[![made-in](https://img.shields.io/badge/made_in-Hong_Kong-cc3399)](#)

> [!CAUTION]
> This project is in its **early stages** and undergoing active development. The API and functionality are **highly unstable** and subject to breaking changes without notice. Outputs are **not guaranteed to be correct** and manual verification is advised. **Use at your own risk.**

**Yumcha** is a declarative, phonology-oriented transliteration engine for Cantonese and other languages.

Rather than maintaining $O(n^2)$ conversion tables between every combination of transcription systems, Yumcha maps schemes to a shared intermediate phonological representation. This allows any supported scheme to be converted into any other with zero glue code.

![Introduction](/docs/media/readme/intro.svg)

Each scheme is defined independently against the language's phonological representation. Adding a new scheme therefore does not require implementing a separate conversion path for every existing scheme.

> "Yumcha" is a play on Cantonese words. While it traditionally means "drinking tea" (<ruby>飲<rt>jam2</rt>茶<rt>caa4</rt>), it also sounds like a "phonological lookup" (<ruby>音<rt>jam1</rt>查<rt>caa4</rt>).
>
> Just as tea brings people together, this engine aims to bridge different transcription and phonetic schemes!

## ✨ Features

- **Shared intermediate representation** — Convert between schemes without maintaining pairwise conversion tables.
- **Declarative scheme definitions** — Define phonologies and transcription schemes as data rather than implementing language-specific conversion logic.
- **Bidirectional conversion** — Convert between a scheme and its intermediate representation in either direction.
- **Scheme-to-scheme conversion** — Convert directly between different schemes within the same language.
- **Constraint-based matching** — Resolve ambiguous and context-dependent representations using indexed constraints.
- **Phonological validation** — Reject combinations that do not conform to the language's defined phonology.
- **Syllable table generation** — Enumerate the valid syllable space and inspect coverage across schemes.
- **Modular & extensible** — Add languages and schemes without modifying the conversion engine.
- **Zero runtime dependencies** — The core engine uses only the Python standard library.
- **Type-hinted** — Built with modern Python 3.12+ type hints for IDE support and readability.

## 🤔 Why Yumcha?

Transcription systems rarely differ only by symbol substitution. They may:

- divide syllables into different components;
- encode tone in different positions or forms;
- distinguish phonological features that another scheme merges;
- use different representations for the same sound;
- impose scheme-specific restrictions on which combinations can be written.

As a result, maintaining pairwise conversion tables becomes increasingly difficult as the number of schemes grows.

For example, with 4 schemes, a pairwise approach requires 6 relationships, while Yumcha's hub-and-spoke approach gives each scheme a relationship with the language's intermediate representation:

![Comparison](/docs/media/readme/why-comparison.svg)

This allows the conversion engine to remain generic while the linguistic details live in the language and scheme definitions.

## 📋 Requirements

Python 3.12 or above.

## 📦 Installation

Yumcha is currently under active development and is not yet a stable release. Install the development version directly from GitHub:

```bash
pip install git+https://github.com/tommycs127/yumcha.git
```

## 🚀 Quick start

Load a bundled language and convert a syllable between schemes:

```python
from yumcha.loader.tsv import load_language

cantonese = load_language("cantonese")

converted = cantonese.convert_scheme_to_scheme(
    source="seot1",
    from_scheme_id="jyutping",
    to_scheme_id="ile",
)

print(str(converted))  # Output: 'soet7'
```

Yumcha performs the conversion through the Cantonese phonology (intermediate representation):

![Conversion](/docs/media/readme/quickstart-conversion.svg)

Conversion results are structured Representation objects rather than plain strings, so their components can also be inspected:

```python
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

## 🔧 Loading languages

Import `load_language()` and load a bundled language by name, or provide a directory containing a custom language definition:

```python
from yumcha.loader.tsv import load_language

# Bundled in the package
cantonese = load_language("cantonese")

# From a custom language directory
colang = load_language(
    "colang",
    directory="/path/to/directory",
)
```

`load_language()` reads the language's phonology and scheme definitions from the supplied resource directory and compiles them into a Language instance.

See [Adding a language and custom schemes](/docs/custom-phonology-and-schemes.md) for the file format and a complete example.

### Adding custom schemes

A custom scheme can be loaded from a TSV file and added to an existing language:

```python
from yumcha.loader.tsv import load_scheme_from_tsv

my_scheme = load_scheme_from_tsv(
  "/path/to/my_scheme.tsv"
)

cantonese.add_scheme(my_scheme)
```

> [!NOTE]
> Custom schemes must conform to the language's underlying phonology. Otherwise, Yumcha will raise an exception when the scheme is added. Consult `Language.phonology` property or the language's source files for the required phonemes and constraints.

## 📚 Working with representations

### Parsing a scheme

`parse_to_scheme()` parses a scheme string into its structured representation:

```python
parsed = cantonese.parse_to_scheme(
    text="chēun",
    scheme_id="yale",
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

Individual components can then be accessed directly:

```python
print(parsed.initial) # Output: 'ch'
print(parsed.coda_consonant) # Output: 'n'
```

### Parsing the intermediate representation

A language's intermediate representation is usually phonological and may use IPA symbols:

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

## 🔄 Conversion

### Scheme to scheme

Convert directly between two schemes:

```python
converted = cantonese.convert_scheme_to_scheme(
    source="seot1",
    from_scheme_id="jyutping",
    to_scheme_id="ile",
)

print(str(converted))  # Output: 'soet7'
```

The result remains a structured representation:

```python
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

### Scheme to intermediate

Convert a scheme representation into the language's intermediate representation:

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

### Intermediate to scheme

Convert an intermediate representation into a scheme:

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

> [!NOTE]
> Conversion methods return a `Representation` subclass rather than a `str`. Use `str()` when a textual representation is needed.

## 📋 Getting available schemes

The schemes registered for a language are available through `Language.schemes`:

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

> [!NOTE]
> `Language.schemes` returns a read-only `dict` view. Avoid printing it directly, as it contains verbose scheme objects.

## 📊 Generating syllable tables

Yumcha can enumerate the valid syllable space defined by a language's phonology and generate representations for its registered schemes.

This is useful for:

- inspecting the syllable inventory;
- comparing scheme coverage;
- finding combinations that a scheme cannot represent;
- validating and reviewing scheme definitions.

Write the full syllable table in TSV format:

```python
from yumcha.exporter import Exporter
from yumcha.loader.tsv import load_language

language_id = "cantonese"
cantonese = load_language(language_id)

exporter = Exporter(
    cantonese,
    loader_fn=load_language,
    loader_args=(language_id,),
)

exporter.export("/path/to/cantonese_syllables.tsv")
```

For non-bundled languages, loader_args can include the custom language directory:

```python
exporter = Exporter(
    cantonese,
    loader_fn=load_language,
    loader_args=(
        language_id,
        "/path/to/directory",
    )
)
```

The exported TSV contains a standard header row and summary rows showing overall syllable counts and scheme coverage percentages.

> [!NOTE]
> Generating and validating the full dataset may take anywhere from a few seconds to a minute depending on your hardware, active schemes, and exporter settings.

### Tracking progress

A progress-bar wrapper can be passed to `progress_bar`:

```python
from tqdm import tqdm

exporter.export(
    "/path/to/cantonese_syllables.tsv",
    progress_bar=tqdm,
)
```

The wrapper must accept a total keyword argument. Libraries such as [`tqdm`](https://tqdm.github.io/) or [`rich.progress`](https://rich.readthedocs.io/en/latest/progress.html) can be used for this purpose.

## 🔤 Supported schemes

> [!NOTE]
> Supported scheme definitions strive to remain faithful to their original designs, but some features and edge cases are not yet implemented.
>
> Pre-generated syllable tables are available in the [`/syllable_tables`](https://github.com/tommycs127/yumcha/tree/main/syllable_tables) directory. These tables are produced by `Exporter.export()` and can be useful for reviewing scheme coverage.
>
> If you spot an error or discrepancy, please [open an issue](https://github.com/tommycs127/yumcha/issues/new). Any help is welcome and appreciated!

### Cantonese

| Scheme name                                           | Example      | Scheme ID         | Note                                                               | Reference                                                                                                                                                                                                        |
| ----------------------------------------------------- | ------------ | ----------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Braille                                               | `⠭⠎⠀`        | `braille`         |                                                                    | [Cantonese Braille](https://en.wikipedia.org/wiki/Cantonese_Braille)                                                                                                                                             |
| Hangul (T. S. Wong Scheme)                            | `츈`         | `hangul`          | Display may vary depending on Unicode combining character support. | [“訓民粵音”──以諺文書寫廣州話之嘗試](http://wongtaksum.no-ip.info:81/index.files/WOC-9_abs.pdf) ([Archive](http://web.archive.org/web/20230522125939/http://wongtaksum.no-ip.info:81/index.files/WOC-9_abs.pdf)) |
| Institute of Language in Education Scheme             | `tsoen1`     | `ile`             |                                                                    | [ILE romanization of Cantonese](https://en.wikipedia.org/wiki/ILE_romanization_of_Cantonese)                                                                                                                     |
| Jyutping                                              | `ceon1`      | `jyutping`        |                                                                    | [Jyutping Cantonese Romanization Scheme](https://lshk.org/jyutping-scheme)                                                                                                                                       |
| Kuping                                                | `tśeon55^1`  | `kuping`          | A romanization scheme I designed!                                  |
| Kuping (Alternative)                                  | `ts'eon55^1` | `kuping_alt`      | An alternative Kuping representation.                              |
| Meyer–Wempe                                           | `ts'un`      | `meyer_wempe`     |                                                                    | [Meyer–Wempe](https://en.wikipedia.org/wiki/Meyer%E2%80%93Wempe)                                                                                                                                                 |
| Pênkyämp                                              | `cönt`       | `penkyamp`        | Glottal stop coda (`q`) is not implemented.                        | [Penkyamp 方案](https://zh-yue.wikipedia.org/wiki/Penkyamp%E6%96%B9%E6%A1%88)                                                                                                                                    |
| Cantonese Transliteration Scheme (Rao's Romanization) | `cên1`       | `rao`             |                                                                    | [Cantonese Transliteration Scheme](https://en.wikipedia.org/wiki/Cantonese_Transliteration_Scheme)                                                                                                               |
| Sidney Lau                                            | `chun1°`     | `sidneylau`       | Tone degree symbol is not superscripted.                           | [Sidney Lau Cantonese Romanization System](https://sidneylau.com/en/sidney-lau-cantonese-romanization-system-pronunciation-guide-initials.htm)                                                                   |
| S. L. Wong (Romanization)                             | `ˈtseun`     | `slwong_roman`    | Conventional numeral tone marking is not implemented.              | [S. L. Wong (romanisation)](<https://en.wikipedia.org/wiki/S._L._Wong_(romanisation)>)                                                                                                                           |
| S. L. Wong (Phonetic)                                 | `ˈtsœn`      | `slwong_phonetic` | Conventional numeral tone marking is not implemented.              | [S. L. Wong (phonetic symbols)](<https://en.wikipedia.org/wiki/S._L._Wong_(phonetic_symbols)>)                                                                                                                   |
| Yale                                                  | `chēun`      | `yale`            |                                                                    | [Yale romanization of Cantonese](https://en.wikipedia.org/wiki/Yale_romanization_of_Cantonese)                                                                                                                   |
| Yựtyựt                                                | `cơn`        | `yutyut`          |                                                                    | [Yựtyựt (越式粵拼)](https://www.omniglot.com/chinese/yutyu.htm)                                                                                                                                                  |

## ⚙️ How it works

Please refer to the [How it works](/docs/how-it-works.md) documentation.

## ⚠️ Limitations

Yumcha currently has limitations at several different levels.

### Linguistic limitations

#### No Tone Sandhi

Tone sandhi depends on linguistic context, such as the surrounding phonological environment. Yumcha currently operates on individual representations and therefore does not model tone sandhi.

### Representational limitations

#### Information loss during conversion

Different schemes may preserve different amounts of phonological information.

For example, Sidney Lau distinguishes high-flat (`1°`) from high-falling (`1`), whereas Jyutping uses `1` for both. Converting from Sidney Lau to Jyutping therefore loses information:

![Information loss during conversion](/docs/media/readme/limitations-information-loss.svg)

Once that distinction has been lost, converting the Jyutping representation back to Sidney Lau cannot determine which original form was intended.

#### Unrepresentable syllables

A scheme may not have a representation for every phonological combination.

For example, S. L. Wong Romanization uses `eu` for `[yː]`, making `[ɛːu̯]` unrepresentable. Converting an input such as `deu6` (Jyutping) to S. L. Wong Romanization therefore produces no valid output.

### Implementation limitations

Some supported schemes are still incomplete. Their individual limitations are noted in the supported-schemes table above and in their scheme definitions.

## ⚙️ How it works

At a high level, Yumcha separates linguistic data from conversion logic.

Language and scheme definitions describe:

- the structure of representations;
- the values allowed in each field;
- phonological constraints;
- mappings between symbols and intermediate forms.

The engine then compiles these definitions into indexed constraints and uses specialized or constraint-based solvers to resolve conversions. This separation means that adding linguistic data does not require writing new conversion algorithms for each language or scheme.

For a detailed explanation of the internal architecture, see [How it works](/docs/how-it-works.md).

## 🧩 Extending Yumcha

Yumcha is designed so that new languages and schemes can primarily be added through data definitions rather than changes to the conversion engine.

### Adding a language

A language definition describes its phonological structure, valid combinations, and available schemes.

See the [tutorial on adding a language](/docs/custom-phonology-and-schemes.md#3-writing-phonologytsv).

### Adding a scheme

A scheme definition describes its representation structure and the mapping between its symbols and the language's intermediate representation.

See the [tutorial on adding a custom scheme](/docs/custom-phonology-and-schemes.md#4-writing-schemestsv).

## 🛣️ Roadmap

### Documentation

- [x] Basic README
- [ ] Architecture documentation
- [x] Tutorial on adding custom languages and schemes
- [x] Scheme definition reference
- [ ] API reference

### Features & Core Engine

- [x] Loading languages and schemes from TSV files
- [x] Scheme parsing and bidirectional conversion
- [x] Syllable table generation and scheme coverage statistics

### Schemes

#### Cantonese

![Cantonese Phonology Progress](https://img.shields.io/badge/Phonology%20file-OK-green)
![Cantonese Progress](<https://img.shields.io/badge/Schemes-14%2F17_(82%25)-gold>)

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

![Mandarin Phonology Progress](https://img.shields.io/badge/Phonology%20file-Pending-red)
![Mandarin Progress](<https://img.shields.io/badge/Schemes-0%2F7_(0%25)-red>)

- [ ] Bopomofo (Zhuyin)
- [ ] Gwoyeu Romatzyh
- [ ] Hanyu Pinyin
- [ ] Palladius (Cyrillization)
- [ ] Tongyong Pinyin
- [ ] Wade–Giles
- [ ] Yale

#### Hokkien

![Hokkien Phonology Progress](https://img.shields.io/badge/Phonology%20file-Pending-red)
![Hokkien Progress](<https://img.shields.io/badge/Schemes-0%2F7_(0%25)-red>)

- [ ] Bbánlám pìngyīm
- [ ] Daī-ghî tōng-iōng pīng-im
- [ ] Modern Literal Taiwanese
- [ ] Pe̍h-ōe-jī
- [ ] Phofsit Daibuun
- [ ] Taiwanese Language Phonetic Alphabet
- [ ] Tâi-lô

## 🙏 Acknowledgments

This project implements transcription and phonetic standards developed by linguists and language communities, whose foundational work made this project possible.

## 📜 License

Yumcha is licensed under the [MIT License](LICENSE).
