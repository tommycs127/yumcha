# 🍵 Yumcha

A phonology-oriented transliteration engine for Cantonese and beyond.

> "Yumcha" is a play on words: while it traditionally means "drinking tea" (<ruby>飲<rp> (</rp><rt>jam2</rt><rp>) </rp>茶<rp> (</rp><rt>caa4</rt><rp>) </rp>), it’s also a phonetic pun for "phonological query" (<ruby>音<rp> (</rp><rt>jam1</rt><rp>) </rp>查<rp> (</rp><rt>caa4</rt><rp>) </rp>). Just as tea brings people together, this engine aims to bridge different transliteration schemes!

## Highlights

- **Universal Bridge:** Uses an underlying phonological representation to convert seamlessly between any two schemes within the same language.
- **Zero Dependencies:** Lightweight and easy to integrate into any project.
- **Modular & Extensible:** Easily add new schemes by implementing a custom parser, disambiguation stages, and composer.
- **Type-hinted:** Built with modern Python type hints for superior IDE support and developer readability.

## How it works

Yumcha parses text into a universal phonological object, which identifies the initial, medial, nucleus, coda, and tone. This allows for faithful conversion between different schemes.

## Installation

Install Yumcha using `pip`:

```bash
pip install git+https://github.com/tommycs127/yumcha.git
```

## Usage

Import the `Yumcha` class from `yumcha` and initialize it:

```py
from yumcha import Yumcha

yumcha = Yumcha()
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

Parse Yale into components:

```py
result = yumcha.parse(
    text="chēun",
    language="cantonese",
    scheme="yale",
)
print(result)  # ParsedYale(initial='ch', nucleus='eu', coda='n', tone='̄')
```

## Supported schemes

### Cantonese

| Scheme name                               | Example  | Scheme code | Note              |
| ----------------------------------------- | -------- | ----------- | ----------------- |
| Institute of Language in Education Scheme | `tsoen1` | `ile`       |                   |
| International Phonetic Alphabet           | `t͡sʰɵn˥` | `ipa`       |                   |
| Jyutping                                  | `ceon1`  | `jyutping`  |                   |
| Sidney Lau                                | `chun1°` | `sidneylau` |                   |
| S. L. Wong                                | `tseun1` | `slwong`    | Romanization only |
| Yale                                      | `chēun`  | `yale`      |                   |

## Requirements

Python 3.12 or above.
