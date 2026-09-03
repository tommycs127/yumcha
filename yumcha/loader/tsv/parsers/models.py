from ....core.primitives.directives import SchemeDirective

CHECK_INTERMEDIATE: set[SchemeDirective] = {
    SchemeDirective.BIDIRECTIONAL,
    SchemeDirective.FORWARD,
}

CHECK_SCHEME: set[SchemeDirective] = {
    SchemeDirective.BIDIRECTIONAL,
    SchemeDirective.REVERSE,
}
