import re

from yumcha.phonology.cantonese import CantoneseConsonant, CantoneseVowel
from yumcha.schemes.cantonese.yale.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    TONE_TO_OBJECT,
)
from yumcha.schemes.regex import get_regex_pattern

INITIALS = list(_ for _ in INITIAL_TO_OBJECT if _ is not None)
NUCLEI = list(_ for _ in NUCLEUS_TO_OBJECT if _ is not None)
CODAS = list(_ for _ in CODA_TO_OBJECT if _ is not None)
CODAS_VOWEL = list(
    set(_ for _ in CODA_TO_OBJECT if isinstance(CODA_TO_OBJECT[_](), CantoneseVowel))
)
CODAS_CONSONANT = list(
    set(
        _ for _ in CODA_TO_OBJECT if isinstance(CODA_TO_OBJECT[_](), CantoneseConsonant)
    )
)
TONES = list(_ for _ in TONE_TO_OBJECT if _ is not None)
TONES_DIACRITICS = list(set(_ for _ in TONES if not _.endswith("h")))
TONES_H = "h"

NUCLEI_WITH_TONE = [
    f"{nucleus[0]}{tone}{nucleus[1:]}"
    for nucleus in NUCLEI
    for tone in TONES_DIACRITICS + [""]
    if nucleus != "yu"
] + [f"yu{tone}" for tone in TONES_DIACRITICS + [""]]

INITIAL_RE = f"({get_regex_pattern(INITIALS)})?"
NUCLEUS_RE = f"({get_regex_pattern(NUCLEI_WITH_TONE)})"
CODA_VOWEL_RE = f"({get_regex_pattern(CODAS_VOWEL)})?"
CODA_CONSONANT_RE = f"({get_regex_pattern(CODAS_CONSONANT)})?"
TONE_H_RE = f"({get_regex_pattern(TONES_H)})?"

REGEX_PATTERN = re.compile(
    f"^{INITIAL_RE}{NUCLEUS_RE}{CODA_VOWEL_RE}{TONE_H_RE}{CODA_CONSONANT_RE}$"
)
