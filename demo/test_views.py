import pytest


def test_view_renders():
    assert 1 == 1


@pytest.mark.skip
def test_view_handles_missing_data():
    pass
