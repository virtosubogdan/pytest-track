import pytest

from pytest_track.models import Module, ItemStatus


@pytest.fixture(name='simple_module')
def simple_module_fixture():
    test_list = ItemStatus('test_list')
    test_dict = ItemStatus('test_dict')
    collections = Module('collections', items=[test_list, test_dict])
    test_repl = ItemStatus('test_repl')
    return Module('python', modules={'collections': collections}, items=[test_repl])


def test_stores_json(simple_module):
    assert simple_module.store_json() == {
        'name': 'python',
        'modules': [{
            'name': 'collections',
            'tests': [{
                'name': 'test_list',
            }, {
                'name': 'test_dict',
            }]
        }],
        'tests': [{
            'name': 'test_repl'
        }]
    }


def test_loads_json():
    pass
