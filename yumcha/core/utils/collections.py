"""Collection utilities and read-only container wrappers.

Provides proxy classes to expose read-only views over internal collections
and sequence structures.
"""

from collections.abc import Iterator, Sequence
from typing import TypeVar, overload, override

T = TypeVar("T")


class SequenceProxy(Sequence[T]):
    """A read-only proxy view over an underlying sequence.

    Wraps a target sequence (e.g., a list) to prevent direct mutations while
    delegating sequence operations like indexing, iteration, and length checks.
    """

    def __init__(self, target_list: Sequence[T]) -> None:
        """Initializes a SequenceProxy instance wrapping the target sequence.

        Args:
            target_list: The underlying sequence to be exposed as a read-only view.
        """
        self._target: Sequence[T] = target_list

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    @override
    def __getitem__(self, index: int | slice) -> T | Sequence[T]:
        """Retrieves an item or slice from the underlying target sequence.

        Args:
            index: An integer index or a slice object.

        Returns:
            The item at the given index, or a subsequence if a slice was provided.
        """
        return self._target[index]

    @override
    def __iter__(self) -> Iterator[T]:
        """Returns an iterator over the underlying target sequence.

        Returns:
            An iterator over the items in the wrapped sequence.
        """
        return iter(self._target)

    @override
    def __len__(self) -> int:
        """Returns the number of elements in the underlying target sequence.

        Returns:
            The total element count of the target sequence.
        """
        return len(self._target)

    @override
    def __repr__(self) -> str:
        """Returns a developer-readable string representation of the SequenceProxy instance.

        Returns:
            A string formatted as `SequenceProxy(<wrapped_sequence>)`.
        """
        return f"SequenceProxy({self._target!r})"
