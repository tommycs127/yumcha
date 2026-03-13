# 🍵 Yumcha

![status](https://badgen.net/badge/status/Early%20development/red)
![Python](https://badgen.net/badge/python/3.12%2B)
[![License](https://badgen.net/badge/license/MIT/orange)](LICENSE)
![type](https://badgen.net/badge/type/Romanization%20engine/cyan)
![made-in](https://badgen.net/badge/made%20in/Hong%20Kong/cc3399)

A phonology-oriented romanization engine for Cantonese and other languages.

> "Yumcha" is a play on Cantonese words. While it traditionally means "drinking tea" (<ruby>飲<rt>jam2</rt>茶<rt>caa4</rt>), it also sounds like "phonological lookup" (<ruby>音<rt>jam1</rt>查<rt>caa4</rt>).
> Just as tea brings people together, this engine aims to bridge different romanization and phonetic schemes!

## ✨ Highlights

- **Scheme-to-Scheme Conversion**: Convert seamlessly between different romanization and phonetic schemes within the same language.
- **Scheme Parsing**: Parse strings to identify their phonological components.
- **Zero Dependencies:** Lightweight and easy to integrate into any project.
- **Type-hinted:** Built with modern Python type hints for better IDE support and readability.
- **Modular & Extensible:** Add new schemes by implementing a custom parser, disambiguation stages, and composer.

## 🤔 Why Yumcha?

Sinitic romanization is fragmented and converting between systems often requires large handwritten mapping tables, which break down for edge cases such as unusual spellings and tone markings.

Yumcha provides a unified API to convert these schemes without writing complex mapping logic or maintaining large mapping tables that can miss edge cases.

## ⚙️ How it works

Yumcha first parses text into an intermediate phonological representation that explicitly identifies components such as the **initial**, **medial**, **nucleus**, **coda**, and **tone**.

Once the syllable is represented in this structured form, it can be re-composed into any supported romanization or phonetic scheme.

## 📋 Requirements

Python 3.12 or above.

## 📦 Installation

Install Yumcha using `pip`:

```bash
pip install git+https://github.com/tommycs127/yumcha.git
```

## 🚀 Usage

Import the `Yumcha` class from `yumcha` and initialize it:

```py
from yumcha import Yumcha

yumcha = Yumcha()
```

### Check available schemes

```py
print(yumcha.available_schemes)  # Or use `yumcha.menu` as a shorthand.
```

Output:

```text
{'cantonese': ['ile', 'ipa', 'jyutping', 'kuping', 'kuping_alt', 'sidneylau', 'slwong_roman', 'slwong_phonetic', 'yale']}
```

### Conversion

Convert Jyutping to IPA:

```py
result = yumcha.convert(
    language="cantonese",
    from_scheme="jyutping",
    to_scheme="ipa",
    text="ceon1",
)
print(result)  # t͡sʰɵn˥
```

### Parsing

Parse a Yale syllable into components:

```py
result = yumcha.parse(
    language="cantonese",
    scheme="yale",
    text="chēun",
)
print(result)
```

Output:

```text
ParsedYale(initial='ch', nucleus='eu', coda='n', tone='̄')
```

### Getting all legal syllables

Get all legal syllables in ILE scheme:

```py
result = yumcha.get_all_legal_syllables(
    language="cantonese",
    scheme="ile",
)
print(result)
```

Output (8,028 items):

```text
['baai1', 'baai2', 'baai3', 'baai4', 'baai5', 'baai6', ..., 'ng1', 'ng2', 'ng3', 'ng4', 'ng5', 'ng6']
```

## 🔤 Supported schemes

### Cantonese

| Scheme name                               | Example      | Scheme code       | Note                                         |
| ----------------------------------------- | ------------ | ----------------- | -------------------------------------------- |
| Institute of Language in Education Scheme | `tsoen1`     | `ile`             |                                              |
| International Phonetic Alphabet           | `t͡sʰɵn˥`     | `ipa`             |                                              |
| Jyutping                                  | `ceon1`      | `jyutping`        |                                              |
| Kuping                                    | `tśeon55^1`  | `kuping`          | A romanization scheme I designed!            |
| Kuping (Alternative)                      | `ts'eon55^1` | `kuping_alt`      | Ditto.                                       |
| Sidney Lau                                | `chun1°`     | `sidneylau`       |                                              |
| S. L. Wong (Romanization)                 | `ˈtseun`     | `slwong_roman`    | Numeral tone marking is **not implemented**. |
| S. L. Wong (Phonetic)                     | `ˈtsœn`      | `slwong_phonetic` | Ditto.                                       |
| Yale                                      | `chēun`      | `yale`            |                                              |

## 🚫 Limitations

### No Tone Sandhi

Tone sandhi depends on linguistic context (e.g., phonological environment and semantic shifts) and is therefore out of scope for this project.

While some schemes include specialized markers for tone sandhi—such as the Sidney Lau scheme, which uses `1°` for the high-flat tone and `1` for the high-falling tone—Yumcha treats these as having the same tone register and name. Consequently, precise information regarding these tonal distinctions may be lost during the scheme-to-scheme conversion.

### Limitations of certain schemes

Some schemes are designed in a way that loses certain phonological distinctions.

For example, the S. L. Wong Romanization scheme uses `eu` for `yː`, which means it cannot represent `ɛːu̯`. Therefore, converting an input such as `deu6` (in Jyutping) to the S. L. Wong Romanization scheme has no valid output.

In such cases, Yumcha will raise `RepresentationError` to indicate that the conversion is impossible.

## 🛣️ Roadmap

### Functionalities

- [x] Conversion
- [x] Parsing
- [x] Generating all legal syllables

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
