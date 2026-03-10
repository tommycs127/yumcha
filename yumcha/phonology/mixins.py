def pretty(obj, indent=0):
    space = "  " * indent

    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            lines.append(f"{space}{k}:")
            lines.append(pretty(v, indent + 1))
        return "\n".join(lines)

    if isinstance(obj, list):
        return "\n".join(pretty(x, indent) for x in obj)

    if obj is None:
        return f"{space}None"

    return f"{space}{obj}"


class PrettyMixin:
    def __str__(self):
        return pretty(self.to_tree())

    def to_tree(self) -> dict:
        return dict()
