import re

from yumcha.schemes.cantonese.kuping.regex import TONE_RE


def parse_tone(text: str) -> tuple[str | None, str | None]:
    m = re.compile(TONE_RE).fullmatch(text)
    if not m:
        return None, None
    tone_letters, tone_category_1, tone_category_2 = m.groups()
    tone_category = tone_category_1 or tone_category_2
    return tone_letters, tone_category
