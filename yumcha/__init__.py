from yumcha.schemes import ParsedScheme
from yumcha.schemes.cantonese.ile import ILE
from yumcha.schemes.cantonese.ipa import IPA as IPACantonese
from yumcha.schemes.cantonese.jyutping import Jyutping
from yumcha.schemes.cantonese.sidneylau import SidneyLau
from yumcha.schemes.cantonese.slwong_phonetic import SLWongPhonetic
from yumcha.schemes.cantonese.slwong_roman import SLWongRoman
from yumcha.schemes.cantonese.yale import Yale


class Yumcha(object):
    @property
    def languages(self) -> dict:
        return {
            "cantonese": {
                "ile": ILE(),
                "ipa": IPACantonese(),
                "jyutping": Jyutping(),
                "sidneylau": SidneyLau(),
                "slwong_roman": SLWongRoman(),
                "slwong_phonetic": SLWongPhonetic(),
                "yale": Yale(),
            }
        }

    def convert(
        self, text: str, language: str, from_scheme: str, to_scheme: str
    ) -> str:
        if language not in self.languages:
            raise ValueError(f'Language "{language}" not found')

        schemes = self.languages[language]

        if from_scheme not in schemes:
            raise ValueError(f'Scheme "{from_scheme}" not found')
        if to_scheme not in schemes:
            raise ValueError(f'Scheme "{to_scheme}" not found')

        text = text.lower().strip()
        reading = schemes[from_scheme].to_underlying(text)
        return schemes[to_scheme].from_underlying(reading)

    def parse(self, text: str, language: str, scheme: str) -> ParsedScheme:
        if language not in self.languages:
            raise ValueError(f'Language "{language}" not found')

        schemes = self.languages[language]

        if scheme not in schemes:
            raise ValueError(f'Scheme "{scheme}" not found')

        return schemes[scheme].to_parsed(text)
