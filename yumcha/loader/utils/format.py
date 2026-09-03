def format_list(items: list[str], conjunction: str = "or", quote: str = '"') -> str:
    """Formats a list of strings into a human-readable list.

    Args:
        items: A list of strings to be formatted.
        conjunction: The word used to join the final item (e.g., "or", "and").
            Defaults to "or".
        quote: The character(s) used to wrap each item. Defaults to '"'.

    Returns:
        A formatted string with quoted items separated by commas and the
        specified conjunction, or an empty string if `items` is empty."""
    quoted = [f"{quote}{item}{quote}" for item in items]

    if not quoted:
        return ""
    if len(quoted) == 1:
        return quoted[0]
    if len(quoted) == 2:
        return f" {conjunction} ".join(quoted)

    return f"{', '.join(quoted[:-1])}, {conjunction} {quoted[-1]}"
