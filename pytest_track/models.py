class Module(object):
    def __init__(self, name):
        self.name = name
        self.tests = []
        self.modules = {}

    def skipped_tests(self):
        return len([x for x in self.tests if x.is_skipped()])

    @property
    def stats(self):
        if hasattr(self, "_stats"):
            return self._stats
        total = len(self.tests)
        ok = total - self.skipped_tests()
        for key, value in self.modules.items():
            child_ok, child_total = value.stats
            ok += child_ok
            total += child_total
        self._stats = (ok, total)
        return self._stats

    def status(self, indent=0):
        ok, total = self.stats
        if self.name:
            print("{}{}, tests {}/{}".format(" " * indent, self.name, ok, total))
        for key, value in self.modules.items():
            value.status(indent + 2)


class ItemStatus(object):
    def __init__(self, node_id, marks=None):
        self.node_id = node_id
        self.marks = marks
        self.status = None

    def is_skipped(self):
        for mark in self.marks:
            if mark.name == "skip":
                return True
        return False

    def __str__(self):
        return "{}: status {}".format(self.node_id, self.status)

    def __repr__(self):
        return self.__str__()
