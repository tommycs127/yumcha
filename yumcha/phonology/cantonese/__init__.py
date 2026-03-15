from dataclasses import dataclass

from yumcha.phonology import (
    Consonant,
    ConsonantManner,
    ConsonantPlace,
    Final,
    Reading,
    Rime,
    Syllable,
    Tone,
    ToneCategory,
    ToneRegister,
    Vowel,
)


class CantoneseConsonantPlace(ConsonantPlace):
    BILABIAL = 1
    LABIODENTAL = 2
    ALVEOLAR = 3
    PALATAL = 4
    VELAR = 5  # [w] included
    GLOTTAL = 6


class CantoneseConsonantManner(ConsonantManner):
    NASAL = 1
    PLOSIVE = 2
    AFFRICATE_SIBILANT = 3
    FRICATIVE_SIBILANT = 4
    FRICATIVE_NON_SIBILANT = 5
    APPROXIMANT = 6  # [w] included
    LATERAL_APPROXIMANT = 7


@dataclass(kw_only=True)
class CantoneseConsonant(
    Consonant[
        CantoneseConsonantPlace,
        CantoneseConsonantManner,
        "CantoneseVowel",
        "CantoneseRime",
    ]
):
    place: CantoneseConsonantPlace
    manner: CantoneseConsonantManner
    aspirated: bool = False
    labialized: bool = False
    syllabic: bool = False  # For [m̩], [ŋ̩]
    checked: bool = False  # For [p̚], [t̚], [k̚]

    @property
    def features(self) -> dict:
        return {
            "place": self.place,
            "manner": self.manner,
            "aspirated": self.aspirated,
            "labialized": self.labialized,
            "syllabic": self.syllabic,
            "checked": self.checked,
        }

    @property
    def features_signature(self) -> tuple:
        return (
            self.place,
            self.manner,
            self.aspirated,
            self.labialized,
            self.syllabic,
            self.checked,
        )

    @property
    def identical_features(self) -> dict:
        return {
            "place": self.place,
            "manner": self.manner,
            "aspirated": self.aspirated,
            "labialized": self.labialized,
        }

    @property
    def identical_features_signature(self) -> tuple:
        return (
            self.place,
            self.manner,
            self.aspirated,
            self.labialized,
        )

    @property
    def RIME_CLASS(self) -> type["CantoneseRime"]:
        return CantoneseRime

    def to_tree(self) -> dict:
        return {self.__class__.__name__: self.__dict__}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


@dataclass(kw_only=True)
class CantoneseVowel(Vowel[CantoneseConsonant, "CantoneseVowel", "CantoneseRime"]):
    @property
    def RIME_CLASS(self) -> type["CantoneseRime"]:
        return CantoneseRime


class CantoneseToneRegister(ToneRegister):
    UNKNOWN = 0
    DARK = 1
    LIGHT = 2
    DARK_UPPER = 3
    DARK_LOWER = 4

    @classmethod
    def base(cls) -> dict:
        return {
            CantoneseToneRegister.UNKNOWN: "Unknown",
            CantoneseToneRegister.DARK: "Dark",
            CantoneseToneRegister.LIGHT: "Light",
            CantoneseToneRegister.DARK_UPPER: "Dark (Upper)",
            CantoneseToneRegister.DARK_LOWER: "Dark (Lower)",
        }


class CantoneseToneCategory(ToneCategory):
    UNKNOWN = 0
    LEVEL = 1
    RISING = 2
    DEPARTING = 3
    ENTERING = 4

    @classmethod
    def base(cls) -> dict:
        return {
            CantoneseToneCategory.UNKNOWN: "Unknown",
            CantoneseToneCategory.LEVEL: "Level",
            CantoneseToneCategory.RISING: "Rising",
            CantoneseToneCategory.DEPARTING: "Departing",
            CantoneseToneCategory.ENTERING: "Entering",
        }


@dataclass(kw_only=True)
class CantoneseTone(Tone[CantoneseToneRegister, CantoneseToneCategory]):
    pass


@dataclass(kw_only=True)
class CantoneseRime(Rime[CantoneseConsonant, CantoneseVowel, "CantoneseFinal"]):
    nucleus: CantoneseConsonant | CantoneseVowel
    coda: CantoneseConsonant | CantoneseVowel | None = None

    def __post_init__(self):
        if isinstance(self.nucleus, CantoneseConsonant):
            if not self.nucleus.syllabic:
                raise ValueError("Only syllabic consonant can be assigned as nucleus")
            if self.nucleus.checked:
                raise ValueError(
                    "Only non-checked consonant can be assigned as nucleus"
                )

        if isinstance(self.nucleus, CantoneseVowel) and self.nucleus.is_semi:
            raise ValueError("Only non-semivowel can be assigned as nucleus")

        if isinstance(self.coda, CantoneseConsonant) and self.coda.syllabic:
            raise ValueError("Only non-syllabic consonant can be assigned as coda")

        if isinstance(self.coda, CantoneseVowel) and not self.coda.is_semi:
            raise ValueError("Only semivowel can be assigned as coda")

        if isinstance(self.nucleus, CantoneseConsonant) and self.coda is not None:
            raise ValueError("Coda cannot appear after consonant nucleus")

        if isinstance(self.nucleus, CantoneseVowel) and self.nucleus.identical_to(
            self.coda
        ):
            raise ValueError("Coda cannot be the same as nucleus")

    @property
    def FINAL_CLASS(self) -> type["CantoneseFinal"]:
        return CantoneseFinal


@dataclass(kw_only=True)
class CantoneseFinal(
    Final[CantoneseConsonant, CantoneseVowel, CantoneseRime, "CantoneseSyllable"]
):
    rime: CantoneseRime
    medial: CantoneseVowel | None = None

    def __post_init__(self):
        if isinstance(self.medial, CantoneseVowel) and not self.medial.is_semi:
            raise ValueError("Only semivowel can be assigned as medial")

    @property
    def SYLLABLE_CLASS(self) -> type["CantoneseSyllable"]:
        return CantoneseSyllable


@dataclass(kw_only=True, init=False)
class CantoneseSyllable(
    Syllable[CantoneseConsonant, CantoneseTone, CantoneseFinal, "CantoneseReading"]
):
    final: CantoneseFinal
    initial: CantoneseConsonant | None = None

    def __post_init__(self):
        if isinstance(self.initial, CantoneseConsonant):
            if self.initial.syllabic:
                raise ValueError(
                    "Only non-syllabic consonant can be assigned as initial"
                )
            if self.initial.identical_to(self.final.rime.nucleus):
                raise ValueError("Nucleus cannot be the same as initial")

    @property
    def TONE_CLASS(self) -> type[CantoneseTone]:
        return CantoneseTone

    @property
    def READING_CLASS(self) -> type["CantoneseReading"]:
        return CantoneseReading


@dataclass(kw_only=True)
class CantoneseReading(Reading[CantoneseSyllable, CantoneseTone]):
    syllable: CantoneseSyllable
    tone: CantoneseTone

    def __post_init__(self):
        if isinstance(self.syllable.final.rime.coda, CantoneseConsonant) and (
            self.syllable.final.rime.coda.checked
            ^ (self.tone.category == CantoneseToneCategory.ENTERING)
        ):
            raise ValueError(
                "Unsupported coda-tone combination (hint: tone sandhi is not supported)"
            )
