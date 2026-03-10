def get_regex_pattern(symbols):
    return "|".join(sorted(symbols, key=len, reverse=True))
