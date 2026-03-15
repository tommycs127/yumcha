from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

from yumcha.phonology.mixins import TreeMixin

ConsonantT = TypeVar("ConsonantT", bound="Consonant")
VowelT = TypeVar("VowelT", bound="Vowel")
ToneT = TypeVar("ToneT", bound="Tone")
ToneRegisterT = TypeVar("ToneRegisterT", bound="ToneRegister")
ToneCategoryT = TypeVar("ToneCategoryT", bound="ToneCategory")
RimeT = TypeVar("RimeT", bound="Rime")
FinalT = TypeVar("FinalT", bound="Final")
SyllableT = TypeVar("SyllableT", bound="Syllable")
ReadingT = TypeVar("ReadingT", bound="Reading")


class ConsonantPlace(Enum):
    pass


class ConsonantManner(Enum):
    pass


ConsonantPlaceT = TypeVar("ConsonantPlaceT", bound="ConsonantPlace")
ConsonantMannerT = TypeVar("ConsonantMannerT", bound="ConsonantManner")


@dataclass(kw_only=True)
class Consonant(
    ABC, TreeMixin, Generic[ConsonantPlaceT, ConsonantMannerT, VowelT, RimeT]
):
    place: ConsonantPlaceT
    manner: ConsonantMannerT

    @property
    @abstractmethod
    def features(self) -> dict:
        return {
            "place": self.place,
            "manner": self.manner,
        }

    @property
    @abstractmethod
    def features_signature(self) -> tuple:
        return (self.place, self.manner)

    @property
    @abstractmethod
    def identical_features(self) -> dict:
        return {
            "place": self.place,
            "manner": self.manner,
        }

    @property
    @abstractmethod
    def identical_features_signature(self) -> tuple:
        return (self.place, self.manner)

    def identical_to(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.identical_features == other.identical_features
        )

    @property
    @abstractmethod
    def RIME_CLASS(self) -> type[RimeT]:
        return Rime  # type: ignore (Base case)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.features == other.features

    def __add__(self, other: VowelT | None) -> RimeT:
        return self.RIME_CLASS(nucleus=self, coda=other)

    def __hash__(self):
        return hash(tuple(sorted(self.features.items())))

    def to_tree(self) -> dict:
        return {self.__class__.__name__: self.__dict__}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(place={self.place!r},manner={self.manner!r})"


class VowelCloseness(Enum):
    CLOSE = 1
    NEAR_CLOSE = 2
    CLOSE_MID = 3
    MID = 4
    OPEN_MID = 5
    NEAR_OPEN = 6
    OPEN = 7


class VowelBackness(Enum):
    FRONT = 1
    NEAR_FRONT = 2
    CENTRAL = 3
    NEAR_BACK = 4
    BACK = 5


@dataclass(kw_only=True)
class Vowel(TreeMixin, Generic[ConsonantT, VowelT, RimeT]):
    closeness: VowelCloseness
    backness: VowelBackness
    rounded: bool
    is_semi: bool = False

    @property
    @abstractmethod
    def features(self) -> dict:
        return {
            "closeness": self.closeness,
            "backness": self.backness,
            "rounded": self.rounded,
            "is_semi": self.is_semi,
        }

    @property
    def features_signature(self) -> tuple:
        return (self.closeness, self.backness, self.rounded, self.is_semi)

    @property
    def identical_features(self) -> dict:
        return {
            "closeness": self.closeness,
            "backness": self.backness,
            "rounded": self.rounded,
        }

    @property
    def identical_features_signature(self) -> tuple:
        return (self.closeness, self.backness, self.rounded)

    def identical_to(self, other: ConsonantT | VowelT | None):
        return (
            isinstance(other, self.__class__)
            and self.identical_features == other.identical_features
        )

    @property
    def RIME_CLASS(self) -> type[RimeT]:
        return Rime  # type: ignore (Base case)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.features == other.features

    def __add__(self, other: ConsonantT | VowelT | None) -> RimeT:
        return self.RIME_CLASS(nucleus=self, coda=other)

    def __hash__(self):
        return hash(tuple(sorted(self.features.items())))

    def to_tree(self) -> dict:
        return {self.__class__.__name__: self.__dict__}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"


class ToneRegister(Enum):
    pass


class ToneCategory(Enum):
    pass


@dataclass(kw_only=True)
class Tone(ABC, TreeMixin, Generic[ToneRegisterT, ToneCategoryT]):
    register: ToneRegisterT
    category: ToneCategoryT
    letters: str | None = None
    # Assign letters only when multiple tones share the same register and category.
    # Treat the Tone object with the letters of None as the "default".

    @property
    def features(self) -> dict:
        return {
            "register": self.register,
            "category": self.category,
            "letters": self.letters,
        }

    @property
    def features_signature(self) -> tuple:
        return (
            self.register,
            self.category,
            self.letters,
        )

    @property
    def phonological_signature(self) -> tuple:
        return (
            self.register,
            self.category,
            None,
        )

    def to_tree(self) -> dict:
        return {self.__class__.__name__: self.features}

    def __eq__(self, other):
        if not isinstance(other, Tone):
            return False
        return self.phonological_signature == other.phonological_signature

    def is_identical_to(self, other):
        if not isinstance(other, Tone):
            return False
        return self.features_signature == other.features_signature

    def __hash__(self):
        return hash(self.phonological_signature)


@dataclass(kw_only=True)
class Rime(ABC, TreeMixin, Generic[ConsonantT, VowelT, FinalT]):
    nucleus: ConsonantT | VowelT
    coda: ConsonantT | VowelT | None = None

    @property
    @abstractmethod
    def FINAL_CLASS(self) -> type[FinalT]:
        return Final  # type: ignore (Base case)

    def __radd__(self, other: VowelT | None) -> FinalT:
        return self.FINAL_CLASS(medial=other, rime=self)

    def to_tree(self) -> dict:
        return {
            "nucleus": self.nucleus.to_tree(),
            "coda": (
                self.coda.to_tree()
                if isinstance(self.coda, (Consonant, Vowel))
                else None
            ),
        }

    def __eq__(self, other):
        if not isinstance(other, Rime):
            return False
        return self.nucleus == other.nucleus and self.coda == other.coda

    def __hash__(self):
        return hash((self.nucleus, self.coda))


@dataclass(kw_only=True)
class Final(ABC, TreeMixin, Generic[ConsonantT, VowelT, RimeT, SyllableT]):
    rime: RimeT
    medial: VowelT | None = None

    @property
    @abstractmethod
    def SYLLABLE_CLASS(self) -> type[SyllableT]:
        return Syllable  # type: ignore (Base case)

    def __radd__(self, initial: ConsonantT | None) -> "Syllable":
        return self.SYLLABLE_CLASS(initial=initial, final=self)

    def to_tree(self) -> dict:
        return {
            "medial": (
                self.medial.to_tree() if isinstance(self.medial, Vowel) else None
            ),
            "rime": self.rime.to_tree(),
        }

    def __eq__(self, other):
        if not isinstance(other, Final):
            return False
        return self.medial == other.medial and self.rime == other.rime

    def __hash__(self):
        return hash((self.medial, self.rime))


@dataclass(kw_only=True)
class Syllable(ABC, TreeMixin, Generic[ConsonantT, ToneT, FinalT, ReadingT]):
    final: FinalT
    initial: ConsonantT | None = None

    @property
    @abstractmethod
    def TONE_CLASS(self) -> type[ToneT]:
        return Tone  # type: ignore (Base case)

    @property
    @abstractmethod
    def READING_CLASS(self) -> type[ReadingT]:
        return Reading  # type: ignore (Base case)

    def __add__(self, tone: "ToneT | None") -> ReadingT:
        if isinstance(tone, self.TONE_CLASS):
            return self.READING_CLASS(syllable=self, tone=tone)

        raise TypeError(
            f"Can only add {type(self).__name__} to {self.TONE_CLASS.__name__}."
        )

    def to_tree(self) -> dict:
        return {
            "initial": (
                self.initial.to_tree() if isinstance(self.initial, Consonant) else None
            ),
            "final": self.final.to_tree(),
        }

    def __eq__(self, other):
        if not isinstance(other, Syllable):
            return False
        return self.initial == other.initial and self.final == other.final

    def __hash__(self):
        return hash((self.initial, self.final))


@dataclass(kw_only=True)
class Reading(TreeMixin, Generic[SyllableT, ToneT]):
    syllable: SyllableT
    tone: ToneT

    def to_tree(self) -> dict:
        return {
            "syllable": self.syllable.to_tree(),
            "tone": self.tone.to_tree(),
        }

    def __eq__(self, other):
        if not isinstance(other, Reading):
            return False
        return self.syllable == other.syllable and self.tone == other.tone

    def __hash__(self):
        return hash((self.syllable, self.tone))
