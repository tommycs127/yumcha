# 🍵 Yumcha

![status](https://badgen.net/badge/status/Alpha%20development/red)
![Python](https://badgen.net/badge/python/3.12%2B)
[![License](https://badgen.net/badge/license/MIT/orange)](LICENSE)
![type](https://badgen.net/badge/type/Romanization%20engine/cyan)
![made-in](https://badgen.net/badge/made%20in/Hong%20Kong/cc3399)

A phonology-oriented romanization engine for Cantonese and other languages.

> "Yumcha" is a play on Cantonese words. While it traditionally means "drinking tea" (<ruby>飲<rt>jam2</rt>茶<rt>caa4</rt>), it also sounds like a "phonological lookup" (<ruby>音<rt>jam1</rt>查<rt>caa4</rt>).
> Just as tea brings people together, this engine aims to bridge different romanization and phonetic schemes!

> [!CAUTION]
> This project is in its **early stages** and undergoing active development. The API and functionality are **highly unstable** and subject to breaking changes without notice. **Do not use this in production environments.**

## ✨ Highlights

- **Scheme-to-Scheme Conversion**: Convert seamlessly between different romanization and phonetic schemes within the same language.
- **Scheme Parsing**: Parse strings to identify their phonological components and their IPA representations.
- **Syllable Set Generation**: Get all valid syllables of a scheme.
- **Zero Third-Party Dependencies:** Lightweight and easy to integrate into any project.
- **Type-hinted**: Built with modern Python 3.12+ type hints for better IDE support and readability.
- **Modular & Extensible**: Add new schemes by simply defining the representation structure, validation rules, and an IPA-to-symbol map!

## 🤔 Why Yumcha?

Sinitic romanization is fragmented and converting between systems often requires large handwritten mapping tables, which break down for edge cases such as unusual spellings and tone markings.

Yumcha provides a unified API to convert these schemes without requiring the user to write complex mapping logic or maintaining large mapping tables that can miss edge cases.

## ⚙️ How it works

Yumcha first parses text into an intermediate phonological representation that explicitly identifies components such as the **initial**, **medial**, **nucleus**, **coda**, and **tone**.

Once the syllable is organized into this structured form, it can be mapped to its IPA representation and subsequently converted into any other supported romanization or phonetic scheme.

## 📋 Requirements

Python 3.12 or above.

## 📦 Installation

Install Yumcha using `pip`:

```bash
pip install git+https://github.com/tommycs127/yumcha.git
```

## 🚀 Usage

Import the `Yumcha` class from `yumcha` and initialize it with `Language` classes:

```py
from yumcha import Yumcha

# Use the bundled languages provided by the library...
from yumcha.languages import Cantonese

# ...or define your own custom subclasses!
# from my_languages import MyLanguage

languages = [
    Cantonese(),
]

yumcha = Yumcha(languages)
```

### Check available schemes

```py
print(yumcha.menu)
```

Output:

```text
{'cantonese': ['ile', 'jyutping', 'kuping', 'kuping_alt', 'sidneylau', 'slwong_phonetic', 'slwong_roman', 'yale']}
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
    nucleus_before_tone='e',
    tone='̄',
    nucleus_after_tone='u',
    coda_vowel='',
    tone_h='',
    coda_consonant='n'
)
```

#### IPA from scheme representation

Parse a Yale syllable into components and retrieve its IPA representation:

```py
parsed_ipa = yumcha.parse_to_ipa(
    language_name="cantonese",
    scheme_name="yale",
    text="chēun",
)
print(repr(parsed_ipa))
```

Output:

```text
CantoneseIPARepresentation(
    initial='t͡sʰ',
    nucleus='ɵ',
    coda='n',
    tone='˥'
)
```

> [!NOTE]
> Parsing methods **do not return a `str` object**, but an instance of a `Representation` subclass. To get a string, simply wrap the object in `str()`:
>
> ```py
> parsed_ipa_str = str(parsed_ipa)
> print(parsed_ipa_str)  # t͡sʰɵn˥
> ```

### Getting all valid syllables

> [!NOTE]
>
> - This operation may take a few seconds to complete due to the volume of validated combinations generated.
> - The output list includes all theoretically valid syllables. While many are rare in common usage, they remain phonologically possible and pronounceable.
> - As validation rules and syllable constraints are updated during development, the total count of the list may fluctuate.

### Phonology

Get all valid syllables via Cantonese phonology:

```py
all_syllables = yumcha.get_all_syllables(
    language_name="cantonese",
)
print(all_syllables)
```

Output (17,780 items):

```text
[CantoneseIPARepresentation(initial='f', nucleus='aː', coda='', tone='˥'),
 CantoneseIPARepresentation(initial='f', nucleus='aː', coda='', tone='˥˧'),
 CantoneseIPARepresentation(initial='f', nucleus='aː', coda='', tone='˧'),
 CantoneseIPARepresentation(initial='f', nucleus='aː', coda='', tone='˧˥'),
 CantoneseIPARepresentation(initial='f', nucleus='aː', coda='', tone='˨'),
 CantoneseIPARepresentation(initial='f', nucleus='aː', coda='', tone='˩'),
 ...,
 CantoneseIPARepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˥˧'),
 CantoneseIPARepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˧'),
 CantoneseIPARepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˧˥'),
 CantoneseIPARepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˨'),
 CantoneseIPARepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˩'),
 CantoneseIPARepresentation(initial='ʔ', nucleus='ʊ', coda='ŋ', tone='˩˧')]
```

### Scheme

Get all valid syllables represented by the Sidney Lau scheme:

```py
all_syllables = yumcha.get_all_syllables(
    language_name="cantonese",
    scheme_name="sidneylau",
)
print(all_syllables)
```

Output (12,600 items):

```text
[SidneyLauRepresentation(initial='f', nucleus='aa', coda='', tone='1°'),
 SidneyLauRepresentation(initial='f', nucleus='aa', coda='', tone='1'),
 SidneyLauRepresentation(initial='f', nucleus='aa', coda='', tone='3'),
 SidneyLauRepresentation(initial='f', nucleus='aa', coda='', tone='2'),
 SidneyLauRepresentation(initial='f', nucleus='aa', coda='', tone='6'),
 SidneyLauRepresentation(initial='f', nucleus='aa', coda='', tone='4'),
 ...,
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='1'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='3'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='2'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='6'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='4'),
 SidneyLauRepresentation(initial='', nucleus='u', coda='ng', tone='5')]
```

## 🔤 Supported schemes

### Cantonese

| Scheme name                               | Example      | Scheme code       | Note                                                  |
| ----------------------------------------- | ------------ | ----------------- | ----------------------------------------------------- |
| Institute of Language in Education Scheme | `tsoen1`     | `ile`             |                                                       |
| Jyutping                                  | `ceon1`      | `jyutping`        |                                                       |
| Kuping                                    | `tśeon55^1`  | `kuping`          | A romanization scheme I designed!                     |
| Kuping (Alternative)                      | `ts'eon55^1` | `kuping_alt`      | Ditto.                                                |
| Sidney Lau                                | `chun1°`     | `sidneylau`       |                                                       |
| S. L. Wong (Romanization)                 | `ˈtseun`     | `slwong_roman`    | Conventional numeral tone marking is not implemented. |
| S. L. Wong (Phonetic)                     | `ˈtsœn`      | `slwong_phonetic` | Ditto.                                                |
| Yale                                      | `chēun`      | `yale`            |                                                       |

## 🚫 Limitations

### No Tone Sandhi

Tone sandhi depends on linguistic context (e.g., phonological environment) and is therefore out of scope for this project.

### Limitations of Certain Schemes

#### Tone Information Loss during Conversion

Some schemes include specialized markers for different tone contours—such as the Sidney Lau scheme, which uses `1°` for the high-flat tone and `1` for the high-falling tone—Yumcha treats these as having the same tone register and name. Consequently, precise information regarding these tonal distinctions may be lost during the scheme-to-scheme conversion.

#### Unrepresentable Syllables

Some schemes are designed in a way that loses certain phonological distinctions.

For example, the S. L. Wong Romanization scheme uses `e` for `[ɛː]` and `u` for `[u̯]`, but it uses `eu` for `[yː]`. This prevents the scheme from being able to represent `[ɛːu̯]`. Therefore, converting an input such as `deu6` (in Jyutping) to the S. L. Wong scheme results in no valid output.

> [!NOTE]
> Such limitations must be explicitly defined in the `validate()` method of any subclass inheriting from the `Representation` class. Without properly defined constraints, exceptions or unexpected results may occur.

## 🛣️ Roadmap

### Documentations

- [x] README.md
- [ ] Tutorial on adding custom languages
- [ ] Tutorial on adding custom schemes

### Functionalities

- [x] Conversion
- [x] Parsing
- [x] Generating all valid syllables

### Schemes

- Cantonese
  - [ ] Barnett–Chao
  - [ ] ~~Bopomofo (Zhuyin) by the Commission on the Unification of Pronunciation~~
    - Will not be implemented until Unicode supports the missing characters.
  - [ ] Bopomofo (Zhuyin) by the People's Government Culture and Education Department
  - [ ] Braille
  - [ ] Cantonese Transliteration Scheme
  - [ ] Hong Kong Government Cantonese Romanization
    - Input mapping will not be implemented due to spelling ambiguities.
  - [x] Institute of Language in Education Scheme
  - [x] International Phonetic Alphabet
  - [x] Jyutping
  - [x] Kuping
  - [ ] Macau Government Cantonese Romanization
    - Input mapping will not be implemented due to spelling ambiguities.
  - [ ] Meyer–Wempe
  - [x] S. L. Wong (Romanization)
  - [x] S. L. Wong (Phonetic)
  - [x] Sidney Lau
  - [ ] Standard Romanisation
  - [x] Yale
  - [ ] Yựtyựt
- Mandarin
  - [ ] Bopomofo (Zhuyin)
  - [ ] Gwoyeu Romatzyh
  - [ ] Hanyu Pinyin
  - [ ] International Phonetic Alphabet
  - [ ] Palladius
  - [ ] Tongyong Pinyin
  - [ ] Wade–Giles
  - [ ] Yale
- Hokkien
  - [ ] International Phonetic Alphabet
  - [ ] Pe̍h-ōe-jī
  - [ ] Phofsit Daibuun
  - [ ] Taiwanese Language Phonetic Alphabet
  - [ ] Tâi-lô

## 🙏 Acknowledgments

This project implements romanization and phonetic standards developed by linguists and language communities, whose foundational work made this project possible.

## 📜 License

Yumcha is licensed under the MIT License. See the [LICENSE file](LICENSE) for the full license text.
