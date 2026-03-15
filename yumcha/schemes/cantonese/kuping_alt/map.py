from yumcha.phonology import (
    VowelBackness,
    VowelCloseness,
)
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseConsonantManner,
    CantoneseConsonantPlace,
    CantoneseTone,
    CantoneseToneCategory,
    CantoneseToneRegister,
    CantoneseVowel,
)
from yumcha.schemes.typing import (
    to_object_map_type,
    to_object_map_type_nucleus,
    to_string_map_type,
)

INITIAL_TO_OBJECT: to_object_map_type = {
    "p": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "p'": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.PLOSIVE,
        aspirated=True,
    ),
    "m": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "f": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.LABIODENTAL,
        manner=CantoneseConsonantManner.FRICATIVE_NON_SIBILANT,
    ),
    "t": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "t'": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        aspirated=True,
    ),
    "n": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "l": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.LATERAL_APPROXIMANT,
    ),
    "k": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "k'": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        aspirated=True,
    ),
    "ng": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "h": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.GLOTTAL,
        manner=CantoneseConsonantManner.FRICATIVE_NON_SIBILANT,
    ),
    "ts": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.AFFRICATE_SIBILANT,
    ),
    "ts'": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.AFFRICATE_SIBILANT,
        aspirated=True,
    ),
    "s": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.FRICATIVE_SIBILANT,
    ),
    "j": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.PALATAL,
        manner=CantoneseConsonantManner.APPROXIMANT,
    ),
    "kw": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        labialized=True,
    ),
    "k'w": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        aspirated=True,
        labialized=True,
    ),
    "w": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.APPROXIMANT,
    ),
    None: lambda: None,
}

OBJECT_TO_INITIAL: to_string_map_type = {
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        False,
    ): "p",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.PLOSIVE,
        True,
        False,
        False,
        False,
    ): "p'",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        False,
        False,
    ): "m",
    (
        CantoneseConsonantPlace.LABIODENTAL,
        CantoneseConsonantManner.FRICATIVE_NON_SIBILANT,
        False,
        False,
        False,
        False,
    ): "f",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        False,
    ): "t",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        False,
        False,
        False,
    ): "t'",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        False,
        False,
    ): "n",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.LATERAL_APPROXIMANT,
        False,
        False,
        False,
        False,
    ): "l",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        False,
    ): "k",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        False,
        False,
        False,
    ): "k'",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        False,
        False,
    ): "ng",
    (
        CantoneseConsonantPlace.GLOTTAL,
        CantoneseConsonantManner.FRICATIVE_NON_SIBILANT,
        False,
        False,
        False,
        False,
    ): "h",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.AFFRICATE_SIBILANT,
        False,
        False,
        False,
        False,
    ): "ts",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.AFFRICATE_SIBILANT,
        True,
        False,
        False,
        False,
    ): "ts'",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.FRICATIVE_SIBILANT,
        False,
        False,
        False,
        False,
    ): "s",
    (
        CantoneseConsonantPlace.PALATAL,
        CantoneseConsonantManner.APPROXIMANT,
        False,
        False,
        False,
        False,
    ): "j",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        True,
        False,
        False,
    ): "kw",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        True,
        False,
        False,
    ): "k'w",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.APPROXIMANT,
        False,
        False,
        False,
        False,
    ): "w",
    None: None,
}

NUCLEUS_TO_OBJECT: to_object_map_type_nucleus = {
    "aa": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "a": lambda: CantoneseVowel(
        closeness=VowelCloseness.NEAR_OPEN,
        backness=VowelBackness.CENTRAL,
        rounded=False,
    ),
    "e": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "oe": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "eo": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.CENTRAL,
        rounded=True,
    ),
    "o": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "i": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "yu": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "u": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "m": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.NASAL,
        syllabic=True,
    ),
    "ng": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.NASAL,
        syllabic=True,
    ),
}

OBJECT_TO_NUCLEUS: to_string_map_type = {
    (VowelCloseness.OPEN, VowelBackness.FRONT, False, False): "aa",
    (VowelCloseness.NEAR_OPEN, VowelBackness.CENTRAL, False, False): "a",
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, False, False): "e",
    (VowelCloseness.CLOSE_MID, VowelBackness.FRONT, False, False): "e",
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, True, False): "oe",
    (VowelCloseness.CLOSE_MID, VowelBackness.CENTRAL, True, False): "eo",
    (VowelCloseness.OPEN_MID, VowelBackness.BACK, True, False): "o",
    (VowelCloseness.CLOSE_MID, VowelBackness.BACK, True, False): "o",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, False, False): "i",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_FRONT, False, False): "i",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, False): "yu",
    (VowelCloseness.CLOSE, VowelBackness.BACK, True, False): "u",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_BACK, True, False): "u",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        True,
        False,
    ): "m",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        True,
        False,
    ): "ng",
}

CODA_TO_OBJECT: to_object_map_type = {
    "i": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=False,
        is_semi=True,
    ),
    "u": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.BACK,
        rounded=True,
        is_semi=True,
    ),
    "m": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "n": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "ng": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "p": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.PLOSIVE,
        checked=True,
    ),
    "t": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        checked=True,
    ),
    "k": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        checked=True,
    ),
    None: lambda: None,
}

OBJECT_TO_CODA: to_string_map_type = {
    (VowelCloseness.CLOSE, VowelBackness.FRONT, False, True): "i",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, True): "i",
    (VowelCloseness.CLOSE, VowelBackness.BACK, True, True): "u",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        False,
        False,
    ): "m",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        False,
        False,
    ): "n",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        False,
        False,
    ): "ng",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        True,
    ): "p",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        True,
    ): "t",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        True,
    ): "k",
    None: None,
}

TONE_TO_OBJECT: to_object_map_type = {
    "^1": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        category=CantoneseToneCategory.LEVEL,
        letters=letters,
    ),
    "^2": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        category=CantoneseToneCategory.RISING,
        letters=letters,
    ),
    "^3": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        category=CantoneseToneCategory.DEPARTING,
        letters=letters,
    ),
    "^4": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.DARK_UPPER,
        category=CantoneseToneCategory.ENTERING,
        letters=letters,
    ),
    "-4": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.DARK_LOWER,
        category=CantoneseToneCategory.ENTERING,
        letters=letters,
    ),
    "_1": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        category=CantoneseToneCategory.LEVEL,
        letters=letters,
    ),
    "_2": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        category=CantoneseToneCategory.RISING,
        letters=letters,
    ),
    "_3": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        category=CantoneseToneCategory.DEPARTING,
        letters=letters,
    ),
    "_4": lambda letters=None: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        category=CantoneseToneCategory.ENTERING,
        letters=letters,
    ),
}

OBJECT_TO_TONE: to_string_map_type = {
    (CantoneseToneRegister.DARK, CantoneseToneCategory.LEVEL, None): "55^1",
    (CantoneseToneRegister.DARK, CantoneseToneCategory.LEVEL, "53"): "53^1",
    (CantoneseToneRegister.DARK, CantoneseToneCategory.RISING, None): "35^2",
    (CantoneseToneRegister.DARK, CantoneseToneCategory.DEPARTING, None): "33^3",
    (CantoneseToneRegister.DARK_UPPER, CantoneseToneCategory.ENTERING, None): "55^4",
    (CantoneseToneRegister.DARK_LOWER, CantoneseToneCategory.ENTERING, None): "33-4",
    (CantoneseToneRegister.LIGHT, CantoneseToneCategory.LEVEL, None): "11_1",
    (CantoneseToneRegister.LIGHT, CantoneseToneCategory.LEVEL, "21"): "21_1",
    (CantoneseToneRegister.LIGHT, CantoneseToneCategory.RISING, None): "13_2",
    (CantoneseToneRegister.LIGHT, CantoneseToneCategory.DEPARTING, None): "22_3",
    (CantoneseToneRegister.LIGHT, CantoneseToneCategory.ENTERING, None): "22_4",
}
