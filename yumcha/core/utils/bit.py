"""Bitwise manipulation and iteration utilities.

Provides functions for efficient operations on integer bitmasks using algorithms
such as Brian Kernighan's bit-counting method.
"""

from collections.abc import Iterator
from typing import Literal, overload


@overload
def iterate_bits(mask: int) -> Iterator[int]: ...


@overload
def iterate_bits(
    mask: int,
    yield_lowest_bit: Literal[False],
) -> Iterator[int]: ...


@overload
def iterate_bits(
    mask: int,
    yield_lowest_bit: Literal[True],
) -> Iterator[tuple[int, int]]: ...


@overload
def iterate_bits(
    mask: int,
    yield_lowest_bit: bool,
) -> Iterator[int] | Iterator[tuple[int, int]]: ...


def iterate_bits(
    mask: int,
    yield_lowest_bit: bool = False,
) -> Iterator[int] | Iterator[tuple[int, int]]:
    """Iterate over set bits (`1`s) in a non-negative integer mask.

    Uses Kernighan's algorithm (`mask &= mask - 1`) to clear the lowest set
    bit on each iteration, executing only as many steps as there are set bits.

    Args:
        mask: A non-negative integer whose set bits will be iterated over.
        yield_lowest_bit: If True, yields tuples of (bit_index, lowest_bit_value).
            If False, yields only the bit_index.

    Yields:
        int: The zero-based index of the set bit (when `yield_lowest_bit` is False).
        tuple[int, int]: A tuple containing (bit_index, lowest_bit_value) where
            lowest_bit_value is 2**bit_index (when `yield_lowest_bit` is True).

    Raises:
        ValueError: If mask is negative.
    """
    if mask < 0:
        raise ValueError("mask must be non-negative")
    while mask:
        lowest_bit = mask & -mask
        bit_index = lowest_bit.bit_length() - 1
        if yield_lowest_bit:
            yield bit_index, lowest_bit
        else:
            yield bit_index
        mask &= mask - 1
