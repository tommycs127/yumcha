from types import EllipsisType

type Pattern = str | EllipsisType
type PatternSequence = tuple[Pattern, ...]
type PatternRegistry = dict[PatternSequence, PatternSequence]
