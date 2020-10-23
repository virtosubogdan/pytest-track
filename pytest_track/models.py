class Module(object):
    def __init__(self, name, items=None, modules=None):
        self.name = name
        self.tests = items or []
        self.modules = modules or {}

    def skipped_tests(self):
        return len([x for x in self.tests if x.is_skipped()])

    @property
    def stats(self):
        if hasattr(self, "_stats"):
            return self._stats
        total = len(self.tests)
        ok = total - self.skipped_tests()
        for key, value in self.modules.items():
            child_ok, child_total, _ = value.stats
            ok += child_ok
            total += child_total
        self._stats = (ok, total, ok * 100 / total)
        return self._stats

    def status(self, indent=0):
        ok, total, percentage = self.stats
        if self.name:
            prefix = "{}{},".format(" " * indent, self.name)
        else:
            prefix = "Total:"
        print("{} {} from {} tests not skipped ({:.2f}%)".format(prefix, ok, total, percentage))
        for key, value in self.modules.items():
            value.status(indent + 2)

    def store_json(self):
        data = {'name': self.name}
        if self.tests:
            data['tests'] = [t.store_json() for t in self.tests]
        if self.modules:
            data['modules'] = [m.store_json() for m in self.modules.values()]
        return data

    @staticmethod
    def load_json(data):
        return Module(
            name=data['name'],
            items=map(ItemStatus.load_json, data.get('tests', [])),
            modules=map(Module.load_json, data.get('modules', []))
        )

    def compare(self, module):
        if self.name != module.name:
            return False
        for own_module, module in zip(self.modules.values(), module.modules.values()):
            if own_module.compare(module):
                return False
        for own_test, test in zip(self.tests, module.tests):
            if own_test.compare(test):
                return False
        return True


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

    def store_json(self):
        return {
            'name': self.node_id
        }

    @staticmethod
    def load_json(data):
        return ItemStatus(data['name'])

    def compare(self, test):
        if self.name != test.name:
            return False
        return True
