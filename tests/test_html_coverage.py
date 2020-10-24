import pytest
from pytest_track.html_coverage import NodeInfo


class Element:
    def __init__(self, e_id="", e_class=None, name="div"):
        self.e_id = e_id
        self.e_class = e_class
        self.name = name

    def get(self, name):
        if name == "id":
            return self.e_id
        if name == "class":
            return self.e_class
        return None


class SeleniumElement:
    def __init__(self, e_id="", e_class=None, name="div"):
        self.e_id = e_id
        self.e_class = e_class
        self.tag_name = name

    def get_attribute(self, name):
        if name == "id":
            return self.e_id
        if name == "class":
            return self.e_class
        return None


@pytest.mark.parametrize(
    "e_id,e_class,name,expected", [("id", ["class", "cl2"], "p", "p#id.class.cl2")]
)
def test_node_rep(e_id, e_class, name, expected):
    assert NodeInfo.rep(Element(e_id, e_class, name)) == expected


def test_node_rep_none():
    assert NodeInfo.rep(None) == ""


@pytest.mark.parametrize(
    "e_id,e_class,name,expected", [("id", "class cl2", "p", "p#id.class.cl2")]
)
def test_node_rep_selenium(e_id, e_class, name, expected):
    element = SeleniumElement(e_id, e_class, name)
    assert NodeInfo.rep_selenium_element(element) == expected


def simple_nodes():
    parent = NodeInfo(name="app")
    child = NodeInfo(name="div#child")
    child2 = NodeInfo(name="div.child2")
    parent[child.name] = child
    parent[child2.name] = child2
    return parent, child, child2


def test_track_element():
    parent, child, child2 = simple_nodes()
    parent.track_find_element("div#child")
    assert child.covered_find == 1
    assert parent.covered_find == 0
    assert child2.covered_find == 0


def test_node_stats():
    parent, child, child2 = simple_nodes()
    parent.track_find_element("div#child")
    cov, covered_find, total, missing = parent.stats()
    assert cov == 0
    assert covered_find == 2
    assert total == 3
    assert missing == [child.name, child2.name, parent.name]
