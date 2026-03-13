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
    "p": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.PLOSIVE,
    ),
    "pʰ": lambda: CantoneseConsonant(
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
    "tʰ": lambda: CantoneseConsonant(
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
    "t͡s": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.AFFRICATE_SIBILANT,
    ),
    "t͡sʰ": lambda: CantoneseConsonant(
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
    "kʷ": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        labialized=True,
    ),
    "kʰʷ": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        aspirated=True,
        labialized=True,
    ),
    "w": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.APPROXIMANT,
    ),
    "ʔ": lambda: None,
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
    ): "pʰ",
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
    ): "tʰ",
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
    ): "kʰ",
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
    ): "t͡s",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.AFFRICATE_SIBILANT,
        True,
        False,
        False,
        False,
    ): "t͡sʰ",
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
    ): "kʷ",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        True,
        True,
        False,
        False,
    ): "kʰʷ",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.APPROXIMANT,
        False,
        False,
        False,
        False,
    ): "w",
    None: "ʔ",
}

NUCLEUS_TO_OBJECT: to_object_map_type = {
    "aː": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "ɐ": lambda: CantoneseVowel(
        closeness=VowelCloseness.NEAR_OPEN,
        backness=VowelBackness.CENTRAL,
        rounded=False,
    ),
    "ɛː": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "e": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "œː": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "ɵ": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.CENTRAL,
        rounded=True,
    ),
    "ɔː": lambda: CantoneseVowel(
        closeness=VowelCloseness.OPEN_MID,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "o": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE_MID,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "iː": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=False,
    ),
    "ɪ": lambda: CantoneseVowel(
        closeness=VowelCloseness.NEAR_CLOSE,
        backness=VowelBackness.NEAR_FRONT,
        rounded=False,
    ),
    "yː": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=True,
    ),
    "uː": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.BACK,
        rounded=True,
    ),
    "ʊ": lambda: CantoneseVowel(
        closeness=VowelCloseness.NEAR_CLOSE,
        backness=VowelBackness.NEAR_BACK,
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
    (VowelCloseness.OPEN, VowelBackness.FRONT, False, False): "aː",
    (VowelCloseness.NEAR_OPEN, VowelBackness.CENTRAL, False, False): "ɐ",
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, False, False): "ɛː",
    (VowelCloseness.CLOSE_MID, VowelBackness.FRONT, False, False): "e",
    (VowelCloseness.OPEN_MID, VowelBackness.FRONT, True, False): "œː",
    (VowelCloseness.CLOSE_MID, VowelBackness.CENTRAL, True, False): "ɵ",
    (VowelCloseness.OPEN_MID, VowelBackness.BACK, True, False): "ɔː",
    (VowelCloseness.CLOSE_MID, VowelBackness.BACK, True, False): "o",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, False, False): "iː",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_FRONT, False, False): "ɪ",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, False): "yː",
    (VowelCloseness.CLOSE, VowelBackness.BACK, True, False): "uː",
    (VowelCloseness.NEAR_CLOSE, VowelBackness.NEAR_BACK, True, False): "ʊ",
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
    "i̯": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=False,
        is_semi=True,
    ),
    "y̯": lambda: CantoneseVowel(
        closeness=VowelCloseness.CLOSE,
        backness=VowelBackness.FRONT,
        rounded=True,
        is_semi=True,
    ),
    "u̯": lambda: CantoneseVowel(
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
    "p̚": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.BILABIAL,
        manner=CantoneseConsonantManner.PLOSIVE,
        checked=True,
    ),
    "t̚": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.ALVEOLAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        checked=True,
    ),
    "k̚": lambda: CantoneseConsonant(
        place=CantoneseConsonantPlace.VELAR,
        manner=CantoneseConsonantManner.PLOSIVE,
        checked=True,
    ),
    None: lambda: None,
}

OBJECT_TO_CODA: to_string_map_type = {
    (VowelCloseness.CLOSE, VowelBackness.FRONT, False, True): "i̯",
    (VowelCloseness.CLOSE, VowelBackness.FRONT, True, True): "y̯",
    (VowelCloseness.CLOSE, VowelBackness.BACK, True, True): "u̯",
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
    ): "p̚",
    (
        CantoneseConsonantPlace.ALVEOLAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        True,
    ): "t̚",
    (
        CantoneseConsonantPlace.VELAR,
        CantoneseConsonantManner.PLOSIVE,
        False,
        False,
        False,
        True,
    ): "k̚",
    None: None,
}

TONE_TO_OBJECT: to_object_map_type = {
    "˥": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.LEVEL,
    ),
    "˥˧": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.LEVEL,
        letters="53",
    ),
    "˧˥": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.RISING,
    ),
    "˧": lambda: CantoneseTone(
        register=CantoneseToneRegister.DARK,
        name=CantoneseToneName.DEPARTING,
    ),
    "˩": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.LEVEL,
    ),
    "˨˩": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.LEVEL,
        letters="21",
    ),
    "˩˧": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.RISING,
    ),
    "˨": lambda: CantoneseTone(
        register=CantoneseToneRegister.LIGHT,
        name=CantoneseToneName.DEPARTING,
    ),
}

OBJECT_TO_TONE: to_string_map_type = {
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, None): "˥",
    (CantoneseToneRegister.DARK, CantoneseToneName.LEVEL, "53"): "˥˧",
    (CantoneseToneRegister.DARK, CantoneseToneName.RISING, None): "˧˥",
    (CantoneseToneRegister.DARK, CantoneseToneName.DEPARTING, None): "˧",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, None): "˩",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.LEVEL, "21"): "˨˩",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.RISING, None): "˩˧",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.DEPARTING, None): "˨",
    (CantoneseToneRegister.DARK_UPPER, CantoneseToneName.ENTERING, None): "˥",
    (CantoneseToneRegister.DARK_LOWER, CantoneseToneName.ENTERING, None): "˧",
    (CantoneseToneRegister.LIGHT, CantoneseToneName.ENTERING, None): "˨",
}
