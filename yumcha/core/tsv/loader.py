from dataclasses import make_dataclass
from importlib.resources.abc import Traversable
from pathlib import PurePath

from ..indexer import Indexer, IntermediateIndexer
from ..models import (
    Phonology,
    Representation,
    Scheme,
    SchemeRowDirective,
)
from ..pattern_tuple import PatternTuple
from ..regexer import Regexer
from .parsers.phonology import parse as parse_phonology
from .parsers.scheme import parse as parse_scheme
from .reader import read


def load_phonology(
    resource: Traversable,
    lang_id: str | None = None,
) -> Phonology:
    if lang_id is None:
        lang_id = PurePath(str(resource)).parent.name

    if not lang_id or not lang_id.isidentifier():
        raise ValueError(f"folder name ({lang_id!r}) must be an identifier")

    headers, data = read(resource)

    context = parse_phonology(headers, data)
    regexer = Regexer(context.charsets)

    class_name = "".join(s.capitalize() for s in lang_id.split("_"))
    fields = [(f, str) for f in context.fields]

    class_ = make_dataclass(
        cls_name=class_name,
        fields=fields,
        frozen=True,
        bases=(Representation,),
    )

    return Phonology(
        lang_id,
        class_,
        context.fields,
        tuple(context.charsets),
        tuple(context.charset_dicts),
        tuple(PatternTuple(p) for p in context.invalid_patterns),
        regexer,
    )


def load_scheme(
    resource: Traversable,
    scheme_id: str | None = None,
) -> Scheme:
    if scheme_id is None:
        filename = resource.name
        scheme_id = filename.rsplit(".", 1)[0]

    if not scheme_id.isidentifier():
        raise ValueError(f"file name ({scheme_id!r}) must be a valid Python identifier")

    headers, data = read(resource)

    context = parse_scheme(headers, data)

    intermediate_indexer = IntermediateIndexer(
        context.intermediate_tuples,
        context.directions,
        {
            SchemeRowDirective.BIDIRECTIONAL,
            SchemeRowDirective.FORWARD,
        },
    )

    scheme_indexer = Indexer(
        context.scheme_tuples,
        context.directions,
        {
            SchemeRowDirective.BIDIRECTIONAL,
            SchemeRowDirective.REVERSE,
        },
    )

    scheme_regexer = Regexer(scheme_indexer.charsets)

    class_name = "".join(s.capitalize() for s in scheme_id.split("_"))
    fields = [(f, str) for f in context.scheme_fields]

    cls = make_dataclass(
        cls_name=class_name,
        fields=fields,
        frozen=True,
        bases=(Representation,),
    )

    return Scheme(
        scheme_id,
        cls,
        context.intermediate_fields,
        intermediate_indexer,
        context.scheme_fields,
        scheme_indexer,
        scheme_regexer,
        context.directions,
    )
