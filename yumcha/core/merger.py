from .indexer import IndexedEntry
from .pattern_tuple import PatternTuple

type Solution = tuple[tuple[int, ...], PatternTuple]
type PriorityKey = tuple[int, ...]


def merge(
    matches: list[IndexedEntry],
) -> list[Solution]:
    if not matches:
        return []

    max_priority: int = len(matches[0][1])
    best_matches: list[Solution] = []

    # Represent priority keys as fast, flat lists where index maps to priority values
    # mapping: priority P -> index (max_priority - P)
    best_priority_key: list[int] = [0] * max_priority

    # 1. PRECOMPUTE LOOKAHEAD (Suffix Counts)
    # suffix_counts[i] will store the total priority counts available from matches[i:]
    num_matches = len(matches)
    suffix_counts = [[0] * max_priority for _ in range(num_matches + 1)]

    for i in range(num_matches - 1, -1, -1):
        # Copy previous counts backward
        for p in range(max_priority):
            suffix_counts[i][p] = suffix_counts[i + 1][p]
        # Increment count for this match's priority
        p_val = matches[i][2]
        if 1 <= p_val <= max_priority:
            suffix_counts[i][max_priority - p_val] += 1

    # Keep a running list of current counts to eliminate Counter allocations entirely
    current_counts = [0] * max_priority

    def backtrack(
        start_idx: int,
        current_pattern_tuple: PatternTuple,
        chosen_indexes: list[int],
    ) -> None:
        nonlocal best_priority_key

        if current_pattern_tuple.is_complete():
            # Standard Python list comparison mimics tuple comparison (element by element)
            if current_counts > best_priority_key:
                best_priority_key = list(current_counts)  # Shallow copy
                best_matches.clear()
                best_matches.append((tuple(chosen_indexes), current_pattern_tuple))
            elif current_counts == best_priority_key:
                best_matches.append((tuple(chosen_indexes), current_pattern_tuple))
            return

        # 2. INSTANT PRUNING CHECK (O(N) vector addition instead of heavy allocations/Counter)
        # Check if the theoretical absolute maximum possible key could even beat our best key
        lookahead = suffix_counts[start_idx]
        for p in range(max_priority):
            max_possible = current_counts[p] + lookahead[p]
            if max_possible < best_priority_key[p]:
                return  # definitely worse, prune branch early
            if max_possible > best_priority_key[p]:
                break  # potentially better, keep going

        for i in range(start_idx, num_matches):
            idx, pattern_tuple, priority = matches[i]

            try:
                new_pattern_tuple = current_pattern_tuple.merge(pattern_tuple)
            except ValueError:  # cannot merge
                continue

            # Mutate state inline
            chosen_indexes.append(idx)
            p_idx = max_priority - priority
            current_counts[p_idx] += 1

            backtrack(
                start_idx=i + 1,
                current_pattern_tuple=new_pattern_tuple,
                chosen_indexes=chosen_indexes,
            )

            # Revert state inline (backtrack step)
            current_counts[p_idx] -= 1
            chosen_indexes.pop()

    initial_pattern_tuple = PatternTuple((...,) * max_priority)

    backtrack(
        start_idx=0,
        current_pattern_tuple=initial_pattern_tuple,
        chosen_indexes=[],
    )

    return best_matches
