from yumcha.phonology import (
    Consonant,
    ConsonantManner,
    ConsonantPlace,
    Final,
    Reading,
    Rime,
    Syllable,
    Tone,
    ToneName,
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


class CantoneseConsonant(Consonant["CantoneseVowel", "CantoneseRime"]):
    def __init__(
        self, place: CantoneseConsonantPlace, manner: CantoneseConsonantManner, **kwargs
    ):
        super().__init__(place=place, manner=manner)
        self.aspirated = kwargs.get("aspirated", False)
        self.labialized = kwargs.get("labialized", False)
        self.syllabic = kwargs.get("syllabic", False)  # For [m̩], [ŋ̩]
        self.checked = kwargs.get("checked", False)  # For [p̚], [t̚], [k̚]

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


class CantoneseToneName(ToneName):
    UNKNOWN = 0
    LEVEL = 1
    RISING = 2
    DEPARTING = 3
    ENTERING = 4

    @classmethod
    def base(cls) -> dict:
        return {
            CantoneseToneName.UNKNOWN: "Unknown",
            CantoneseToneName.LEVEL: "Level",
            CantoneseToneName.RISING: "Rising",
            CantoneseToneName.DEPARTING: "Departing",
            CantoneseToneName.ENTERING: "Entering",
        }


class CantoneseTone(Tone[CantoneseToneRegister, CantoneseToneName]):
    pass


class CantoneseRime(Rime[CantoneseConsonant, CantoneseVowel, "CantoneseFinal"]):
    def __init__(
        self,
        nucleus: CantoneseConsonant | CantoneseVowel,
        coda: CantoneseConsonant | CantoneseVowel | None = None,
    ):
        if isinstance(nucleus, CantoneseConsonant):
            if not nucleus.syllabic:
                raise ValueError("Only syllabic consonant can be assigned as nucleus")
            if nucleus.checked:
                raise ValueError(
                    "Only non-checked consonant can be assigned as nucleus"
                )

        if isinstance(nucleus, CantoneseVowel) and nucleus.is_semi:
            raise ValueError("Only non-semivowel can be assigned as nucleus")

        if isinstance(coda, CantoneseConsonant) and coda.syllabic:
            raise ValueError("Only non-syllabic consonant can be assigned as coda")

        if isinstance(coda, CantoneseVowel) and not coda.is_semi:
            raise ValueError("Only semivowel can be assigned as coda")

        if isinstance(nucleus, CantoneseConsonant) and coda is not None:
            raise ValueError("Coda cannot appear after consonant nucleus")

        if isinstance(nucleus, CantoneseVowel) and nucleus.identical_to(coda):
            raise ValueError("Coda cannot be the same as nucleus")

        super().__init__(nucleus=nucleus, coda=coda)

    @property
    def FINAL_CLASS(self) -> type["CantoneseFinal"]:
        return CantoneseFinal


class CantoneseFinal(
    Final[CantoneseConsonant, CantoneseVowel, CantoneseRime, "CantoneseSyllable"]
):
    def __init__(self, rime: CantoneseRime, medial: CantoneseVowel | None = None):
        if isinstance(medial, CantoneseVowel) and not medial.is_semi:
            raise ValueError("Only semivowel can be assigned as medial")

        super().__init__(rime=rime, medial=medial)

    @property
    def SYLLABLE_CLASS(self) -> type["CantoneseSyllable"]:
        return CantoneseSyllable


class CantoneseSyllable(
    Syllable[CantoneseConsonant, CantoneseTone, CantoneseFinal, "CantoneseReading"]
):
    def __init__(
        self, final: CantoneseFinal, initial: CantoneseConsonant | None = None
    ):
        if isinstance(initial, CantoneseConsonant):
            if initial.syllabic:
                raise ValueError(
                    "Only non-syllabic consonant can be assigned as initial"
                )
            if initial.identical_to(final.rime.nucleus):
                raise ValueError("Nucleus cannot be the same as initial")

        super().__init__(final=final, initial=initial)

    @property
    def TONE_CLASS(self) -> type[CantoneseTone]:
        return CantoneseTone

    @property
    def READING_CLASS(self) -> type["CantoneseReading"]:
        return CantoneseReading


class CantoneseReading(Reading[CantoneseSyllable, CantoneseTone]):
    def __init__(self, syllable: CantoneseSyllable, tone: CantoneseTone):
        self.syllable = syllable
        self.tone = tone

        if isinstance(syllable.final.rime.coda, CantoneseConsonant) and (
            syllable.final.rime.coda.checked ^ (tone.name == CantoneseToneName.ENTERING)
        ):
            raise ValueError(
                "Unsupported coda-tone combination (hint: tone sandhi is not supported)"
            )
