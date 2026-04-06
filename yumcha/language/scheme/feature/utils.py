from types import EllipsisType

from .types import FeatureTuple


def weak_union_tuples(t1: tuple, t2: tuple) -> tuple:
    # Ensure they are the same length
    if len(t1) != len(t2):
        raise ValueError("tuples must be of the same length to union by index")

    # Pick the non-Ellipsis value, defaulting to t1's value
    return tuple(v2 if isinstance(v1, EllipsisType) else v1 for v1, v2 in zip(t1, t2))


def union_tuples(t1: FeatureTuple, t2: FeatureTuple) -> tuple:
    if len(t1) != len(t2):
        raise ValueError("tuples must be of the same length to union by index.")

    result = []
    for i, (v1, v2) in enumerate(zip(t1, t2)):
        v1_is_ellipsis = isinstance(v1, EllipsisType)
        v2_is_ellipsis = isinstance(v2, EllipsisType)

        if not v1_is_ellipsis and not v2_is_ellipsis:
            if v1 != v2:
                raise ValueError(
                    f"conflict at index {i}: cannot merge {v1!r} and {v2!r}"
                )
            result.append(v1)
        elif v1_is_ellipsis:
            result.append(v2)
        else:
            result.append(v1)

    return tuple(result)
