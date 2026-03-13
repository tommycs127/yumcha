from yumcha.phonology import (
    VowelBackness,
    VowelCloseness,
)
from yumcha.phonology.cantonese import (
    CantoneseConsonant,
    CantoneseConsonantManner,
    CantoneseConsonantPlace,
    CantoneseTone,
    CantoneseToneName,
    CantoneseToneRegister,
    CantoneseVowel,
)
from yumcha.schemes.typing import to_object_map_type, to_string_map_type

INITIAL_TO_OBJECT: to_object_map_type = {
    "b": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "p": lambda: CantoneseConsonant(
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
    "d": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "t": lambda: CantoneseConsonant(
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
    "g": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "k": lambda: CantoneseConsonant(
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
    "j": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.AFFRICATE_SIBILANT,
    ),
    "ch": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.AFFRICATE_SIBILANT,
        aspirated=True,
    ),
    "s": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.FRICATIVE_SIBILANT,
    ),
    "y": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.PALATAL,
        manner=CantoneseConsonantManner.APPROXIMANT,
    ),
    "gw": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        labialized=True,
    ),
    "kw": lambda: CantoneseConsonant(
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
    ): "b",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.PLOSIVE,
        True,
        False,
        False,
        False,
    ): "p",
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
    ): "d",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        False,
        False,
        False,
    ): "t",
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
    ): "g",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        False,
        False,
        False,
    ): "k",
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
    ): "j",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.AFFRICATE_SIBILANT,
        True,
        False,
        False,
        False,
    ): "ch",
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
    ): "y",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        True,
        False,
        False,
    ): "gw",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        True,
        False,
        False,
    ): "kw",
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

NUCLEUS_TO_OBJECT: to_object_map_type = {
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
    "eu": lambda: None,  # For search only
    "euh": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "u": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.CENTRAL,
        rounded=True,
    ),
    "oh": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "o": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "i": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "ue": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "oo": lambda: CantoneseVowel(
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
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, True, False): "euh",
    (VowelCloseness.CLOSE_MID, VowelBackness.CENTRAL, True, False): "u",
    (VowelCloseness.OPEN_MID, VowelBackness.BACK, True, False): "oh",
    (VowelCloseness.CLOSE_MID, VowelBackness.BACK, True, False): "o",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, False, False): "i",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_FRONT, False, False): "i",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, False): "ue",
    (VowelCloseness.CLOSE, VowelBackness.BACK, True, False): "oo",
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
    "1°": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.LEVEL,
    ),
    "1": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.LEVEL,
        letters="53",
    ),
    "1*": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.LEVEL,
        letters="35",
    ),
    "2": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.RISING,
    ),
    "2°": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.RISING,
        letters="55",
    ),
    "3": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.DEPARTING,
    ),
    "3°": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.DEPARTING,
        letters="55",
    ),
    "3*": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.DEPARTING,
        letters="35",
    ),
    "4": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.LEVEL,
    ),
    "4°": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.LEVEL,
        letters="55",
    ),
    "4*": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.LEVEL,
        letters="35",
    ),
    "5": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.RISING,
    ),
    "5°": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.RISING,
        letters="55",
    ),
    "5*": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.RISING,
        letters="35",
    ),
    "6": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.DEPARTING,
    ),
    "6°": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.DEPARTING,
        letters="55",
    ),
    "6*": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.DEPARTING,
        letters="35",
    ),
}

OBJECT_TO_TONE: to_string_map_type = {
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, None): "1°",
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, "53"): "1",
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, "35"): "1*",
    (CantoneseToneRegister.DARK, CantoneseToneName.RISING, None): "2",
    (CantoneseToneRegister.DARK, CantoneseToneName.RISING, "55"): "2°",
    (CantoneseToneRegister.DARK, CantoneseToneName.DEPARTING, None): "3",
    (CantoneseToneRegister.DARK, CantoneseToneName.DEPARTING, "55"): "3°",
    (CantoneseToneRegister.DARK, CantoneseToneName.DEPARTING, "35"): "3*",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, None): "4",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, "55"): "4°",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, "35"): "4*",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.RISING, None): "5",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.RISING, "55"): "5°",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.RISING, "35"): "5*",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.DEPARTING, None): "6",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.DEPARTING, "55"): "6°",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.DEPARTING, "35"): "6*",
    (CantoneseToneRegister.DARK_UPPER, CantoneseToneName.ENTERING, None): "1",
    (CantoneseToneRegister.DARK_UPPER, CantoneseToneName.ENTERING, "35"): "1*",
    (CantoneseToneRegister.DARK_LOWER, CantoneseToneName.ENTERING, None): "3",
    (CantoneseToneRegister.DARK_LOWER, CantoneseToneName.ENTERING, "35"): "3*",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.ENTERING, None): "6",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.ENTERING, "35"): "6*",
}
