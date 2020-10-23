import mock

from pytest_track.plugin import pytest_configure, TrackReport


def test_configure_plugin():
    mock_config = mock.Mock()
    mock_config.getoption.side_effect = lambda name: name == "track"
    pytest_configure(mock_config)
    assert mock_config._track.config == mock_config
    mock_config.pluginmanager.register.assert_called_once_with(mock_config._track)


def test_configure_plugin_not_request():
    mock_config = mock.Mock()
    mock_config.getoption.side_effect = lambda name: False
    pytest_configure(mock_config)
    mock_config.pluginmanager.register.assert_not_called()


def test_item_collection():
    pass
