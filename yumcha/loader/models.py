from ..core.primitives.directives import SchemeDirective

FROM_INTERMEDIATE: set[SchemeDirective] = {
    SchemeDirective.BIDIRECTIONAL,
    SchemeDirective.FORWARD,
}

FROM_SCHEME: set[SchemeDirective] = {
    SchemeDirective.BIDIRECTIONAL,
    SchemeDirective.REVERSE,
}
