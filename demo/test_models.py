import pytest


def test_model_creation():
    assert 1 == 1


@pytest.mark.skip
def test_model_method():
    pass


class TestSpecialModel:
    def test_special_create(self):
        pass

    @pytest.mark.skip
    def test_handles_error(self):
        raise Exception("not implemented")

    def test_special_validation(self):
        assert 2 == 2
