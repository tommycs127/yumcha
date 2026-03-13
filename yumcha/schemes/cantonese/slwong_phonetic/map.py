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
from yumcha.schemes.typing import (
    to_object_map_type,
    to_object_map_type_nucleus,
    to_string_map_type,
)

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
    "k": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "kʰ": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        aspirated=True,
    ),
    "ŋ": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.NASAL,
    ),
    "h": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.GLOTTAL,
        manner=CantoneseConsonantManner.FRICATIVE_NON_SIBILANT,
    ),
    "dz": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.AFFRICATE_SIBILANT,
    ),
    "ts": lambda: CantoneseConsonant(
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
    ): "ŋ",
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
    ): "dz",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.AFFRICATE_SIBILANT,
        True,
        False,
        False,
        False,
    ): "ts",
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

NUCLEUS_TO_OBJECT: to_object_map_type_nucleus = {
    "a": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "ɐ": lambda: CantoneseVowel(
        closeness=VowelCloseness.NEAR_OPEN,
        backness=VowelBackness.CENTRAL,
        rounded=False,
    ),
    "ɛ": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "e": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "œ": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "ɔ": lambda: CantoneseVowel(
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
    "y": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "u": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "m̩": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.NASAL,
        syllabic=True,
    ),
    "ŋ̩": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.NASAL,
        syllabic=True,
    ),
}

OBJECT_TO_NUCLEUS: to_string_map_type = {
    (VowelCloseness.OPEN, VowelBackness.FRONT, False, False): "a",
    (VowelCloseness.NEAR_OPEN, VowelBackness.CENTRAL, False, False): "ɐ",
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, False, False): "ɛ",
    (VowelCloseness.CLOSE_MID, VowelBackness.FRONT, False, False): "e",
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, True, False): "œ",
    (VowelCloseness.CLOSE_MID, VowelBackness.CENTRAL, True, False): "œ",
    (VowelCloseness.OPEN_MID, VowelBackness.BACK, True, False): "ɔ",
    (VowelCloseness.CLOSE_MID, VowelBackness.BACK, True, False): "o",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, False, False): "i",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_FRONT, False, False): "i",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, False): "y",
    (VowelCloseness.CLOSE, VowelBackness.BACK, True, False): "u",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_BACK, True, False): "u",
    (
        CantoneseConsonantPlace.BILABIAL,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        True,
        False,
    ): "m̩",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.NASAL,
        False,
        False,
        True,
        False,
    ): "ŋ̩",
}

CODA_TO_OBJECT: to_object_map_type = {
    "i": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=False,
        is_semi=True,
    ),
    "y": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=True,
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
    "ŋ": lambda: CantoneseConsonant(
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
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, True): "y",
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
    ): "ŋ",
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
    "ˈ": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.LEVEL,
    ),
    "ˊ": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.RISING,
    ),
    "ˉ": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.DEPARTING,
    ),
    "ˌ": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.LEVEL,
    ),
    "ˏ": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.RISING,
    ),
    "ˍ": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.DEPARTING,
    ),
}

OBJECT_TO_TONE: to_string_map_type = {
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, None): "ˈ",
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, "53"): "ˈ",
    (CantoneseToneRegister.DARK, CantoneseToneName.RISING, None): "ˊ",
    (CantoneseToneRegister.DARK, CantoneseToneName.DEPARTING, None): "ˉ",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, None): "ˌ",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, "21"): "ˌ",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.RISING, None): "ˏ",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.DEPARTING, None): "ˍ",
    (CantoneseToneRegister.DARK_UPPER, CantoneseToneName.ENTERING, None): "ˈ",
    (CantoneseToneRegister.DARK_LOWER, CantoneseToneName.ENTERING, None): "ˉ",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.ENTERING, None): "ˍ",
}
