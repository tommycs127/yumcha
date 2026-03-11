# 🍵 Yumcha

A phonology-oriented transliteration engine for Cantonese and other languages.

> "Yumcha" is a play on Cantonese words. While it traditionally means "drinking tea" (<ruby>飲<rt>jam2</rt>茶<rt>caa4</rt>), it also sounds like "phonological lookup" (<ruby>音<rt>jam1</rt>查<rt>caa4</rt>).
> Just as tea brings people together, this engine aims to bridge different Cantonese transliteration schemes!

## ✨ Highlights

- **Scheme-to-Scheme Conversion**: Convert seamlessly between different Cantonese romanization and phonetic schemes.
- **Scheme Parsing**: Parse strings to identify their phonological components.
- **Zero Dependencies:** Lightweight and easy to integrate into any project.
- **Type-hinted:** Built with modern Python type hints for better IDE support and readability.
- **Modular & Extensible:** Easily add new schemes by implementing a custom parser, disambiguation stages, and composer.

## 🤔 Why Yumcha?

Cantonese romanization is fragmented and converting between systems often requires large handwritten mapping tables, which break down for edge cases such as ambiguous finals or tone markings.

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

```py
{'cantonese': ['ile', 'ipa', 'jyutping', 'sidneylau', 'slwong_roman', 'slwong_phonetic', 'yale']}
```

### Conversion

Convert Jyutping to IPA:

```py
result = yumcha.convert(
    text="ceon1",
    language="cantonese",
    from_scheme="jyutping",
    to_scheme="ipa",
)
print(result)  # t͡sʰɵn˥
```

### Parsing

Parse a Yale syllable into components:

```py
result = yumcha.parse(
    text="chēun",
    language="cantonese",
    scheme="yale",
)
print(result)
```

Output:

```py
ParsedYale(initial='ch', nucleus='eu', coda='n', tone='̄')
```

## 🔤 Supported schemes

### Cantonese

| Scheme name                               | Example  | Scheme code       | Note                                         |
| ----------------------------------------- | -------- | ----------------- | -------------------------------------------- |
| Institute of Language in Education Scheme | `tsoen1` | `ile`             |                                              |
| International Phonetic Alphabet           | `t͡sʰɵn˥` | `ipa`             |                                              |
| Jyutping                                  | `ceon1`  | `jyutping`        |                                              |
| Sidney Lau                                | `chun1°` | `sidneylau`       |                                              |
| S. L. Wong (Romanization)                 | `ˈtseun` | `slwong_roman`    | Numeral tone marking is **not implemented**. |
| S. L. Wong (Phonetic)                     | `ˈtsœn`  | `slwong_phonetic` | Ditto.                                       |
| Yale                                      | `chēun`  | `yale`            |                                              |

## 🚫 Limitations

### No Tone Sandhi

Tone sandhi depends on linguistic context and is therefore difficult to implement.

### Limitations of certain schemes

Some schemes are designed in a way that loses certain phonological distinctions.

For example, the S. L. Wong Romanization scheme uses `eu` for `yː`, which means it cannot represent `ɛːu̯`. Therefore, converting an input such as `deu6` (in Jyutping) to the S. L. Wong Romanization scheme has no valid output.

In such cases, Yumcha will raise `RepresentationError` to indicate that the conversion is impossible.

## 🛣️ Roadmap

### Schemes

- Cantonese
  - [ ] Hong Kong Government Cantonese Romanisation
    - Parsing will not be implemented due to ambiguous spelling.
  - [x] Institute of Language in Education Scheme
  - [x] International Phonetic Alphabet
  - [x] Jyutping
  - [ ] Macau Government Cantonese Romanization
    - Parsing will not be implemented due to ambiguous spelling.
  - [x] Sidney Lau
  - [x] S. L. Wong (Romanization)
  - [x] S. L. Wong (Phonetic)
  - [x] Yale
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

Yumcha is licensed under the MIT License. See the LICENSE file for the full license text.
