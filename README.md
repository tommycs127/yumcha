# 🍵 Yumcha

A phonology-oriented transliteration engine for Cantonese and beyond.

## Highlights

- **Universal Bridge:** Uses an underlying phonological representation to convert between any two schemes seamlessly.
- **Zero Dependencies:** Light-weight and easy to integrate.
- **Modular & Extensible:** Define your own schemes by implementing the base classes.
- **Type-Hinted**: For better IDE support and developer experience.

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

To convert Jyutping to IPA:

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

To see the parsed Yale:

```py
result = yumcha.parse(
    text="chēun",
    language="cantonese",
    scheme="yale",
)
print(result)  # ParsedYale(initial='ch', nucleus='eu', coda='n', tone='̄')
```

## Supported schemes

- Cantonese

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
