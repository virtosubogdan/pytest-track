import pytest

from pytest_track.models import ItemStatus, Module


@pytest.fixture()
def simple_module():
    skip = pytest.mark.skip.mark
    random_mark = pytest.mark.random_mark.mark
    test1 = ItemStatus("test1", [skip])
    test2 = ItemStatus("test2", [random_mark])
    module = Module("test_module")
    module.tests.append(test1)
    module.tests.append(test2)
    root = Module("")
    root.modules["test_module"] = module
    return root
