from ...primitives.directives import SchemeRowDirective

CHECK_INTERMEDIATE: set[SchemeRowDirective] = {
    SchemeRowDirective.BIDIRECTIONAL,
    SchemeRowDirective.FORWARD,
}

CHECK_SCHEME: set[SchemeRowDirective] = {
    SchemeRowDirective.BIDIRECTIONAL,
    SchemeRowDirective.REVERSE,
}
