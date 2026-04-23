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
- [**Syllable Set Generation**](#getting-all-valid-syllables): Get all valid syllables via the phonology of the language or as represented by a specific scheme.
- **Zero Third-Party Dependencies:** Lightweight and easy to integrate into any project.
- **Type-hinted**: Built with modern Python 3.12+ type hints for better IDE support and readability.
- **Modular & Extensible**: Add new schemes by simply defining the representation structure, validation rules, and an intermediate-to-symbol map!

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

Import the `Yumcha` class from `yumcha` and the built-in language classes from `yumcha.languages`:

```py
from yumcha import Yumcha

# Use the bundled languages provided by the library...
from yumcha.languages import Cantonese

# ...or define your own custom subclasses!
from my_languages import MyLanguage
```

Then, pass the initialized language instances into the `Yumcha` constructor:

```py
languages = [
    Cantonese(),
    MyLanguage(),
]

yumcha = Yumcha(languages)
```

`Yumcha` registers these instances in an internal dictionary, using the lowercase name of each language class as the key. For example, `Cantonese` is indexed as `"cantonese"`, and `MyLanguage` becomes `"mylanguage"`. This same indexing logic applies to `Scheme` instances within each language.

#### Registering custom schemes

> [!NOTE]
> Custom schemes must conform to the language's underlying phonology; otherwise, `Yumcha` will raise a `PhonologyError` during initialization. Consult the `yumcha.languages.<language>.phonology` module for required phonemes.

Use `Language.add()` method to register custom schemes before initialization:

```py
from my_scheme import MyScheme

cantonese = Cantonese()
cantonese.add_scheme(MyScheme)

languages = [cantonese]

yumcha = Yumcha(languages)
```

### Getting available schemes

```py
print(yumcha.menu)
```

Output:

```text
{
    'cantonese': [
        'braille',
        'hangul'
        'ile',
        ...,
        'slwong_roman',
        'yale',
        'yutyut'
    ]
}
```

### Conversion

Convert a Jyutping syllable to ILE:

```py
converted = y.convert(
    language_name="cantonese",
    from_scheme_name="jyutping",
    to_scheme_name="ile",
    text="seot1",
)
print(converted)  # soet7
```

### Parsing

> [!NOTE]
> Parsing methods **do not return a `str` object**, but an instance of a `Representation` subclass. To get a string, simply wrap the object in `str()`.

#### Scheme representation

Parse a Yale syllable into components:

```py
parsed = yumcha.parse(
    language_name="cantonese",
    scheme_name="yale",
    text="chēun",
)
print(repr(parsed))
```

Output:

```text
YaleRepresentation(
    initial='ch',
    nucleus_before_tone_diacritic='e',
    tone_diacritic='̄',
    nucleus_after_tone_diacritic='u',
    coda_vowel='',
    tone_h='',
    coda_consonant='n'
)
```

#### Intermediate representation from scheme

Parse a Yale syllable into components and retrieve its intermediate representation:

```py
parsed_intermediate = yumcha.parse_to_intermediate(
    language_name="cantonese",
    scheme_name="yale",
    text="chēun",
)
print(repr(parsed_intermediate))
```

Output:

```text
CantoneseRepresentation(
    initial='t͡sʰ',
    nucleus='ɵ',
    coda='n',
    tone='˥'
)
```

### Getting all valid syllables

> [!NOTE]
>
> - The output list includes all theoretically valid syllables. While many are rare in common usage, they remain phonologically possible and pronounceable.
> - As validation rules and syllable constraints are updated during development, the total count of the list may fluctuate.

#### Phonology

Get all valid syllables via Cantonese phonology:

```py
all_syllables = yumcha.get_all_syllables(
    language_name="cantonese",
)
print(all_syllables)
```

Output (20,776 items):

```text
[CantoneseRepresentation(initial='f', nucleus='aː', coda='', tone='˥'),
 CantoneseRepresentation(initial='f', nucleus='aː', coda='', tone='˥˧'),
 CantoneseRepresentation(initial='f', nucleus='aː', coda='', tone='˧'),
 ...,
 CantoneseRepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˨'),
 CantoneseRepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˩'),
 CantoneseRepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˩˧')]
```

#### Scheme

Get all valid syllables represented by the Sidney Lau scheme:

```py
all_syllables = yumcha.get_all_syllables(
    language_name="cantonese",
    scheme_name="sidneylau",
)
print(all_syllables)
```

Output (10,626 items):

```text
[SidneyLauRepresentation(initial='f', nucleus='a', coda='', tone='1°'),
 SidneyLauRepresentation(initial='f', nucleus='a', coda='', tone='1'),
 SidneyLauRepresentation(initial='f', nucleus='a', coda='', tone='3')
 ...,
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='6'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='4'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='5')]
```

### Calculating the coverage of a scheme

> [!NOTE]
>
> - This function may take a few seconds to complete due to the high volume of combinations generated.
> - This function iterates through all valid syllables; refer to the notes in the [Getting all valid syllables](#getting-all-valid-syllables) section for further details.

Calculate the phonological coverage of the Meyer–Wempe scheme:

```py
coverage = yumcha.get_coverage(
    language_name="cantonese",
    scheme_name="meyer_wempe",
)
print(coverage)  # 0.5068348093954563
```

The closer this value is to `1`, the more phonologically complete the scheme's design is.

## 🔤 Supported schemes

> [!NOTE]
> While I've done my best to keep the supported schemes true to their original design, some syllables may be incorrectly handled due to existing constraints.
>
> You can review the generated syllable tables in [this directory](https://github.com/tommycs127/yumcha/tree/main/syllable_tables) (be sure to read the [specifications](https://github.com/tommycs127/yumcha/blob/main/syllable_tables/specs.md) first). These tables are produced by the `generate_syllable_table()` method within the `Yumcha` instance.
>
> If you spot any errors, please [open an issue](https://github.com/tommycs127/yumcha/issues/new). Any help is welcome and appreciated!

### Cantonese

| Scheme name                                           | Example      | Scheme code       | Note                                                                                              |
| ----------------------------------------------------- | ------------ | ----------------- | ------------------------------------------------------------------------------------------------- |
| Braille                                               | `⠭⠎⠀`        | `braille`         |                                                                                                   |
| Hangul (T. S. Wong Scheme)                            | `츈`         | `hangul`          | Some characters may not display correctly due to the limitations of Unicode combining characters. |
| Institute of Language in Education Scheme             | `tsoen1`     | `ile`             |                                                                                                   |
| Jyutping                                              | `ceon1`      | `jyutping`        |                                                                                                   |
| Kuping                                                | `tśeon55^1`  | `kuping`          | A romanization scheme I designed!                                                                 |
| Kuping (Alternative)                                  | `ts'eon55^1` | `kuping_alt`      | Ditto.                                                                                            |
| Meyer–Wempe                                           | `ts'un`      | `meyer_wempe`     |                                                                                                   |
| Pênkyämp                                              | `cönt`       | `penkyamp`        | The letter `q` as a coda for the glottal stop `[ʔ]` is not implemented.                           |
| Cantonese Transliteration Scheme (Rao's Romanization) | `cên1`       | `rao`             |                                                                                                   |
| Sidney Lau                                            | `chun1°`     | `sidneylau`       | Tones are not superscripted as it is impossible to superscript the degree symbol.                 |
| S. L. Wong (Romanization)                             | `ˈtseun`     | `slwong_roman`    | Conventional numeral tone marking is not implemented.                                             |
| S. L. Wong (Phonetic)                                 | `ˈtsœn`      | `slwong_phonetic` | Ditto.                                                                                            |
| Yale                                                  | `chēun`      | `yale`            |                                                                                                   |
| Yựtyựt                                                | `cơn`        | `yutyut`          |                                                                                                   |

## ⚙️ How it works

Yumcha functions as a bridge between diverse transcription systems by utilizing a structured, phonology-driven engine. Instead of simple string replacement, it processes language through four distinct layers:

- **Phonology Definition**: Languages are defined by their internal sound structures. This creates a universal format that bridges different schemes much like IPA.

- **Sequential Text Parsing**: Input text is decomposed into its orthographical components using fine-grained regular expressions. This ensures that even complex diacritics and combining characters are identified accurately.

- **Context-Aware Conversion**: Yumcha maps these parsed components to the Intermediate Representation. This process is context-aware, meaning it can prioritize specific phonological or orthographical rules over literal translations, ensuring linguistic accuracy.

- **Bidirectional Mapping**: Because the system is built on reversible logic, the intermediate format can be seamlessly converted into any supported target scheme, preserving all relevant phonological information.

For a detailed breakdown of the code implementation and mapping logic, please refer to the [How it works](/docs/how-it-works.md) documentation.

## 🚫 Limitations

### No Tone Sandhi

Tone sandhi depends on linguistic context (e.g., phonological environment) and is therefore out of scope for this project.

### Limitations of Certain Schemes

#### Information Loss during Conversion

Some schemes include specialized symbols for historical phonemes or detailed tone contours. For example, the Sidney Lau scheme distinguishes between the high-flat tone (`1°`) and the high-falling tone (`1`). In contrast, other schemes lack this distinction; in Jyutping, `1` represents both contours, where the high level tone is assumed by default. Consequently, this precise tonal granularity may be lost during scheme-to-scheme conversion.

#### Unrepresentable Syllables

Some schemes are designed in a way that loses certain phonological distinctions.

For example, the S. L. Wong Romanization scheme uses `e` for `[ɛː]` and `u` for `[u̯]`, but it uses `eu` for `[yː]`. This prevents the scheme from being able to represent `[ɛːu̯]`. Therefore, converting an input such as `deu6` (in Jyutping) to the S. L. Wong scheme results in no valid output.

## 🛣️ Roadmap

### Documentations

- [x] README.md
- [ ] How it works documentation
- [ ] Tutorial on adding custom languages
- [ ] Tutorial on adding custom schemes

### Functionalities

- [x] Conversion
- [x] Parsing
- [x] Generating all valid syllables
- [x] Calculating the coverage of a scheme

### Schemes

#### Cantonese

![](https://us-central1-progress-markdown.cloudfunctions.net/progress/14?&label=14/17&min=0&max=17)

- [ ] Barnett–Chao
- [ ] ~~Bopomofo (Zhuyin) by the Commission on the Unification of Pronunciation~~
  - Will not be implemented until Unicode supports the missing characters.
- [ ] Bopomofo (Zhuyin) by the People's Government Culture and Education Department
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
- [ ] Standard Romanisation
- [x] Yale
- [x] Yựtyựt

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

Yumcha is licensed under the MIT License. See the [LICENSE file](LICENSE) for the full license text.
