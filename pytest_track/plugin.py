from .models import Module, ItemStatus
from .confluence import report_to_confluence


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--track",
        action="store",
        dest="track",
        default=None,
        help="Specifies how to track test implementation.",
    )


def pytest_configure(config):
    track_option = config.getoption("track")
    if track_option:
        # xdist concern TODO
        config._track = TrackReport(config)
        config.pluginmanager.register(config._track)


def pytest_unconfigure(config):
    track = getattr(config, "_track", None)
    if not track:
        return
    track_type = config.getvalue("track")
    if track_type == "confluence":
        report_to_confluence(track, config)
    else:
        track.tests.status()
    del config._track
    config.pluginmanager.unregister(track)


class TrackReport(object):
    def __init__(self, config):
        self.config = config
        self.tests = Module("")

    def pytest_itemcollected(self, item):
        module_paths = item.module.__name__.split(".")
        module_status = self.tests
        for path in module_paths:
            module_status = module_status.modules.setdefault(path, Module(path))
        if hasattr(item.obj, "pytestmark"):
            marks = item.obj.pytestmark
        else:
            marks = []
        module_status.tests.append(ItemStatus(item.nodeid, marks))
