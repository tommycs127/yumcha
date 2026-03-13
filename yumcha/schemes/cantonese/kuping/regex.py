import re

from yumcha.schemes.cantonese.kuping.map import (
    CODA_TO_OBJECT,
    INITIAL_TO_OBJECT,
    NUCLEUS_TO_OBJECT,
)
from yumcha.schemes.regex import get_regex_pattern

INITIALS = list(_ for _ in INITIAL_TO_OBJECT if _ is not None)
NUCLEI = list(_ for _ in NUCLEUS_TO_OBJECT if _ is not None)
CODAS = list(_ for _ in CODA_TO_OBJECT if _ is not None)

TONE_LETTERS = ["55", "53", "35", "33", "11", "21", "13", "22"]
TONE_REGISTERS = [r"\^", "-", "_"]
TONE_NAMES = ["1", "2", "3", "4"]

INITIAL_RE = f"({get_regex_pattern(INITIALS)})?"
NUCLEUS_RE = f"({get_regex_pattern(NUCLEI)})"
CODA_RE = f"({get_regex_pattern(CODAS)})?"
TONE_LETTER_RE = f"({get_regex_pattern(TONE_LETTERS)})"
TONE_REGISTER_RE = f"(?:{get_regex_pattern(TONE_REGISTERS)})"
TONE_NAME_RE = f"(?:{get_regex_pattern(TONE_NAMES)})"
REGEX_PATTERN = re.compile(
    f"^{INITIAL_RE}{NUCLEUS_RE}{CODA_RE}({TONE_LETTER_RE}({TONE_REGISTER_RE}{TONE_NAME_RE})?|({TONE_REGISTER_RE}{TONE_NAME_RE}))$"
)
