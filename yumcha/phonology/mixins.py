class TreeMixin:
    def __str__(self):
        return str(self.to_tree())

    def to_tree(self) -> dict:
        return dict()
