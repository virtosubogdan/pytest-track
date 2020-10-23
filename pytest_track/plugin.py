from datetime import datetime
import logging

from .models import Module, ItemStatus
from .confluence import report_to_confluence
from .html_coverage import HTMLData

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption(
        "--track",
        action="store",
        dest="track",
        default=None,
        help="Specifies how to track test implementation.",
    )
    group.addoption(
        "--html-cov",
        action="store",
        dest="html_cov",
        default=None,
        help="Calculate HTML coverage for this directory",
    )
    group.addoption(
        "--html-cov-cache",
        action="store_true",
        dest="html_cov_cache",
        default=False,
        help="Use cache (does not re-read HTML files from disk)",
    )
    group.addoption(
        "--html-cov-show-elements",
        action="store_true",
        dest="html_cov_show_elements",
        default=False,
        help="Show elements that are not covered",
    )


def pytest_configure(config):
    track_option = config.getoption("track")
    if track_option:
        # xdist concern TODO
        config._track = TrackReport(config)
        config.pluginmanager.register(config._track)
    html_cov = config.getoption("html_cov")
    if html_cov:
        data = None
        if config.getoption("html_cov_cache"):
            logger.info('Using pytest-track HTML coverage cache')
            data = config.cache.get('pytest-track-html-cache', {})
        show_missed_elements = config.getoption("html_cov_show_elements")
        config._track_html = HTMLData(html_cov, data, show_missed_elements)
        config.pluginmanager.register(config._track_html, name='pytest-track-html-coverage')


def pytest_unconfigure(config):
    track_unconfigure(config)
    html_coverate_unconfigure(config)


def html_coverate_unconfigure(config):
    html_cov = getattr(config, "_track_html", None)
    if not html_cov:
        return
    html_cov.stats()
    config.cache.set('pytest-track-html-coverage', html_cov.to_json())
    del config._track_html
    config.pluginmanager.unregister(html_cov)


def track_unconfigure(config):
    track = getattr(config, "_track", None)
    if not track:
        return
    track_type = config.getvalue("track")
    if track_type == "confluence":
        report_to_confluence(track, config)
    else:
        # track.tests.status()
        pass
    key = datetime.now().microsecond
    data = config.cache.get('pytest-track', {})
    if data:
        latest = max(data.keys())
        old_result = data[latest]
        old_module = Module.load_json(old_result)
        changed = old_module.compare(track.tests)
        if not changed:
            print('Status not changed. Removing old status')
            del data[latest]
    data[key] = track.tests.store_json()
    config.cache.set('pytest-track', data)
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
