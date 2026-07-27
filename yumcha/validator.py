from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .core.exceptions import ConflictingMatchError, PhonologicalError
from .core.models import Pattern, Scheme, SchemeRowDirective
from .core.pattern_tuple import PatternTuple

if TYPE_CHECKING:
    from .language import Language


class Validator:
    @classmethod
    def validate(
        cls,
        language: Language,
        scheme: Scheme,
        pattern_tuple: PatternTuple,
        used_indexes: set[int],
        as_: Literal["intermediate", "scheme"],
        strict: bool = True,
    ) -> bool:
        args = (
            language,
            scheme,
            pattern_tuple,
            used_indexes,
            "intermediate" if as_ == "scheme" else "scheme",
            strict,
        )

        return cls.validate_phonotactics(*args) and cls.validate_roundtrip(*args)

    @classmethod
    def validate_phonotactics(
        cls,
        language: Language,
        scheme: Scheme,
        pattern_tuple: PatternTuple,
        used_indexes: set[int],
        as_: Literal["intermediate", "scheme"] = "intermediate",
        strict: bool = True,
    ) -> bool:
        used_mask = 0
        for idx in used_indexes:
            used_mask |= 1 << idx

        for invalid_idx, invalid_mask in enumerate(
            scheme.intermediate_indexer.invalid_masks
        ):
            invalid_pattern_tuple = language.phonology.invalid_patterns[invalid_idx]
            intersected_mask = used_mask & invalid_mask

            # The invalid_mask contains all scheme indices matching the invalid pattern.
            # We check if the number of intercepted bits is greater or equal to the
            # required constraint weight (occupancy) of the original phonological pattern.
            is_possible_match = (
                intersected_mask.bit_count() >= invalid_pattern_tuple.priority
            )

            if is_possible_match:
                intersected_indexes = cls._get_set_bits(intersected_mask)

                try:
                    collided = cls._get_collided_patterns(
                        scheme,
                        pattern_tuple,
                        invalid_pattern_tuple,
                        intersected_indexes,
                        strict=strict,
                    )
                    if collided is None:  # False positive: Type mismatch
                        continue
                except TypeError:  # Ditto
                    continue

                if not strict:
                    return False

                components = (
                    f"{tuple(collided)} [Phonologic: {invalid_pattern_tuple}]"
                    if as_ == "scheme"
                    else f"{invalid_pattern_tuple}"
                )

                raise PhonologicalError(
                    f"phonologically invalid pattern tuple {pattern_tuple}.\n"
                    f"Violating components found: {components}\n"
                    f"Review the phonology definition or the scheme design."
                )

        return True

    @staticmethod
    def validate_roundtrip(
        language: Language,
        scheme: Scheme,
        pattern_tuple: PatternTuple,
        expected_indexes: set[int],
        as_: Literal["intermediate", "scheme"],
        strict: bool = True,
    ) -> bool:
        pattern_tuple_str = pattern_tuple.to_string()
        parsed = (
            language.parse_as_scheme(scheme.id, pattern_tuple_str)
            if as_ == "scheme"
            else language.parse_as_intermediate(pattern_tuple_str)
        )

        roundtripped, roundtripped_indexes = language._find_best_result(
            scheme, PatternTuple(parsed), as_, strict
        )

        if roundtripped is None:
            return False

        is_stable_pair = (
            roundtripped_indexes.issubset(expected_indexes)
            if as_ == "scheme"
            else expected_indexes.issubset(roundtripped_indexes)
        )

        if not is_stable_pair:
            # No need to raise an error if any unidirectional conversion is present
            for expected_idx in expected_indexes:
                direction = scheme.directions[expected_idx]
                if direction is not SchemeRowDirective.BIDIRECTIONAL:
                    return False

            if not strict:
                return False

            indexes_intersect = roundtripped_indexes.intersection(expected_indexes)

            cause_indexes = expected_indexes - indexes_intersect

            source_indexer, target_indexer = (
                (scheme.indexer, scheme.intermediate_indexer)
                if as_ == "scheme"
                else (scheme.intermediate_indexer, scheme.indexer)
            )

            expected_parsed = PatternTuple((...,)) * source_indexer.pattern_tuple_length
            cause_pt = PatternTuple((...,)) * target_indexer.pattern_tuple_length

            for idx in cause_indexes:
                expected_parsed = expected_parsed.merge(
                    source_indexer.pattern_tuples_raw[idx]
                )
                cause_pt = cause_pt.merge(target_indexer.pattern_tuples_raw[idx])

            stable_pt = roundtripped.filter(cause_pt.occupancy)

            cause_pt_str = cause_pt.to_debug_msg()
            stable_pt_str = stable_pt.to_debug_msg()
            expected_parsed_str = expected_parsed.to_string(True)

            raise ConflictingMatchError(
                f"expected pattern {cause_pt_str} "
                f"from text '{pattern_tuple_str}', "
                f"got {stable_pt_str}\n"
                f"To resolve this ambiguity, "
                f"review the design of scheme '{scheme.id}' "
                f"and explicitly add {cause_pt_str} as its own entry, "
                "ensuring its associated pattern does not conflict "
                f"with text '{expected_parsed_str}'."
            )

        return True

    @staticmethod
    def _get_set_bits(mask: int) -> list[int]:
        indexes = []
        add_index = indexes.append

        while mask > 0:
            # Isolate the lowest set bit (e.g., 0b10100 -> 0b00100)
            lowest_bit = mask & -mask

            # Get its 0-based index using bit_length
            add_index(lowest_bit.bit_length() - 1)

            # Clear the lowest set bit (Brian Kernighan's step: mask & (mask - 1))
            mask &= mask - 1

        return indexes

    @staticmethod
    def _get_collided_patterns(
        scheme: Scheme,
        pattern_tuple: PatternTuple,
        invalid_pattern_tuple: PatternTuple,
        intersected_indexes: list[int],
        strict: bool = True,
    ) -> tuple[Pattern, ...] | None:
        violated = PatternTuple((...,)) * len(pattern_tuple)

        for idx in intersected_indexes:
            violated = violated.merge(scheme.indexer.pattern_tuples_raw[idx])

        collided: list[Pattern] = [Ellipsis] * len(pattern_tuple)

        for (idx, component), im_indexes in zip(
            enumerate(violated), scheme.fields.values()
        ):
            for im_idx in im_indexes:
                im_component = invalid_pattern_tuple[im_idx]

                component_is_str = type(component) is str
                im_component_is_str = type(im_component) is str

                if im_component_is_str and not component_is_str:
                    if not strict:
                        return None
                    raise TypeError(
                        f"expected component type at index {idx} to be str, "
                        f"got {type(component).__name__}"
                    )

                if invalid_pattern_tuple[im_idx] is not ...:
                    collided[im_idx] = component

        return tuple(collided)
