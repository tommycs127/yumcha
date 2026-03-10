import re

from schemes.cantonese.jyutping.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
    TONE_TO_OBJECT,
)
from schemes.regex import get_regex_pattern

INITIALS = list(_ for _ in INITIAL_TO_OBJECT if _ is not None)
NUCLEI = list(_ for _ in NUCLEUS_TO_OBJECT if _ is not None)
CODAS = list(_ for _ in CODA_TO_OBJECT if _ is not None)
TONES = list(_ for _ in TONE_TO_OBJECT if _ is not None)

INITIAL_RE = f"({get_regex_pattern(INITIALS)})?"
NUCLEUS_RE = f"({get_regex_pattern(NUCLEI)})"
CODA_RE = f"({get_regex_pattern(CODAS)})?"
TONE_RE = f"({get_regex_pattern(TONES)})"
REGEX_PATTERN = re.compile(f"^{INITIAL_RE}{NUCLEUS_RE}{CODA_RE}{TONE_RE}$")
