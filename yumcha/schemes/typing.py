from typing import Any, Callable, Mapping, TypedDict

to_object_map_type = Mapping[str | None, Callable[..., Any]]
to_string_map_type = Mapping[tuple | None, str | None]


class SchemeMap(TypedDict):
    initial_to_object: to_object_map_type
    medial_to_object: to_object_map_type
    nucleus_to_object: to_object_map_type
    coda_to_object: to_object_map_type
    tone_to_object: to_object_map_type

    object_to_initial: to_string_map_type
    object_to_medial: to_string_map_type
    object_to_nucleus: to_string_map_type
    object_to_coda: to_string_map_type
    object_to_tone: to_string_map_type
