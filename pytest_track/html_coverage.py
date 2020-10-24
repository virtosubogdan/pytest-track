import os
from itertools import takewhile
import logging

from bs4 import BeautifulSoup

try:
    import selenium
    from selenium.webdriver import Chrome
except:

    class Chrome:
        def __init__(self):
            raise Exception("Selenium is not available")


from tabulate import tabulate

logger = logging.getLogger(__name__)


class NodeInfo(dict):
    def __init__(self, element=None, name=None):
        super().__init__()
        self.name = self.rep(element) if not name else name
        self.covered = 0
        self.covered_find = 0

    @staticmethod
    def rep(element):
        if not element:
            return ""
        name = element.name
        e_id = element.get("id")
        if e_id:
            name += "#{}".format(e_id)
        e_class = element.get("class")
        if e_class:
            name = ".".join([name, *e_class])
        return name

    @staticmethod
    def rep_selenium_element(element):
        name = element.tag_name
        e_id = element.get_attribute("id")
        if e_id:
            name += "#{}".format(e_id)
        e_class = element.get_attribute("class")
        if e_class:
            name += "." + e_class.replace(" ", ".")
        return name

    def __str__(self):
        return "(NodeInfo {})".format(self.name)

    def track(self, path_list, element):
        e_rep = self.rep(element)
        logger.debug("track %s %s %s", self, e_rep, path_list)
        if e_rep == self.name:
            self.covered += 1
            return
        for child in self.values():
            child.track(path_list, element)

    def track_find_element(self, element_rep):
        logger.debug("track_find_element %s %s", self.name, element_rep)
        if element_rep == self.name:
            self.covered_find += 1
        for child in self.values():
            child.track_find_element(element_rep)

    def stats(self):
        cov = 0
        covered_find = 0
        total = 1 if self.name else 0  # Root elements
        missing = []
        for child_name, child in self.items():
            c_cov, c_cov_find, c_total, c_missing = child.stats()
            cov += c_cov
            covered_find += c_cov_find
            total += c_total
            missing.extend(c_missing)
        if (cov > 0 or self.covered > 0) and self.name:
            # considered covered if children are covered
            cov += 1
        if cov == 0:
            missing.append(self.name)
        if (covered_find > 0 or self.covered_find > 0) and self.name:
            covered_find += 1
        logger.debug("NodeInfo stats %s %s/%s %s", self.name, cov, total, missing)
        return cov, covered_find, total, missing

    def debug(self, indent=""):
        logger.debug("%s %s %s", indent, self.name, self.stats())
        for child in self.values():
            child.debug(indent + "  ")

    def to_json(self):
        return {
            "node_name": self.name,
            "children": [child.to_json() for child in self.values()],
        }

    @staticmethod
    def from_json(data):
        node = NodeInfo(name=data["node_name"])
        for child_data in data["children"]:
            child = NodeInfo.from_json(child_data)
            node[child.name] = child
        return node


class FileData:
    def __init__(self, filename):
        self.filename = filename
        self.tree = NodeInfo()

    def stats(self):
        return self.tree.stats()

    def to_json(self):
        return {"short_name": self.filename, "tree": self.tree.to_json()}

    @staticmethod
    def from_json(data):
        file_data = FileData(data["short_name"])
        file_data.tree = NodeInfo.from_json(data["tree"])
        return file_data


class HTMLData:
    def __init__(self, file, data=None, show_missed_elements=False):
        self.files = {}
        self.common_prefix = None
        self.show_missed_elements = show_missed_elements
        self._stats = []
        self._total_cov = 0
        self._total_cov_find = 0
        if data:
            cached_files = {
                file_data["filename"]: FileData.from_json(file_data["data"])
                for file_data in data
            }
        else:
            cached_files = {}

        for root, dirnames, filenames in os.walk(file):
            for filename in filenames:
                if not filename.endswith(".html"):
                    continue
                full_filename = os.path.join(root, filename)
                if full_filename in cached_files:
                    self.files[full_filename] = cached_files[full_filename]
                else:
                    with open(full_filename) as handle:
                        soup = BeautifulSoup(handle.read(), "html.parser")
                        data = FileData(filename)
                        self.files[full_filename] = data
                        self.parse(data.tree, soup)

        strings = self.files.keys()
        self.common_prefix = "".join(
            c[0] for c in takewhile(lambda x: all(x[0] == y for y in x), zip(*strings))
        )

    def to_json(self):
        return [
            {"filename": filename, "data": data.to_json()}
            for filename, data in self.files.items()
        ]

    def parse(self, tree: NodeInfo, soup):
        for child in soup.children:
            if not child.name:
                continue
            if self.is_relevant(child):
                rep = NodeInfo.rep(child)
                tree[rep] = NodeInfo(child)
                self.parse(tree[rep], child)
            else:
                self.parse(tree, child)

    def cover(self, html):
        soup = BeautifulSoup(html, "html.parser")
        self.cover_element([], soup, [])

    @staticmethod
    def is_relevant(element):
        if not element.name:
            return False
        if element.get("id"):
            return True
        if element.get("class"):
            return True
        if element.name.startswith("app"):
            return True
        return False

    def cover_element(self, path_list, element, existing_matches):
        for child in element.children:
            if not child.name:
                continue
            if self.is_relevant(child):
                self.track(path_list, child, existing_matches)
                new_path = [*existing_matches, NodeInfo.rep(element)]
                self.cover_element(new_path, child, existing_matches)
            else:
                self.cover_element(path_list, child, existing_matches)

    def track(self, path_list, element, existing_matches):
        for tree in existing_matches:
            tree.track(path_list, element)
        for data in self.files.values():
            data.tree.track(path_list, element)

    def called_find_element(self, element):
        element_rep = NodeInfo.rep_selenium_element(element)
        logger.debug("called_find_element %s", element_rep)
        for data in self.files.values():
            data.tree.track_find_element(element_rep)

    def stats(self, should_print=True):
        self._stats = []
        covered = 0
        covered_find = 0
        total = 0
        for filename, data in self.files.items():
            current_cov, current_cov_find, current_total, missing = data.stats()
            if not current_total:
                # Empty file
                continue
            covered += current_cov
            covered_find += current_cov_find
            total += current_total
            avg = (
                round(current_cov / current_total * 100, 1) if current_total else "N/A"
            )
            avg_find = (
                round(current_cov_find / current_total * 100, 1)
                if current_total
                else "N/A"
            )
            filename = filename[len(self.common_prefix) :]
            if self.show_missed_elements:
                self._stats.append([filename, avg, avg_find, missing])
            else:
                self._stats.append([filename, avg, avg_find])
        self._total_cov = covered / total * 100
        self._total_cov_find = covered_find / total * 100
        if should_print:
            print(tabulate(self._stats))
            print("Total HTML coverage:", round(self._total_cov, 3))
            print("Total HTML inspected elements:", round(self._total_cov_find, 3))


class TrackCoverageChrome(Chrome):
    def __init__(self, request, *args, **kwargs):
        self.pytest_config = request.config
        self.plugin = self.pytest_config.pluginmanager.get_plugin(
            "pytest-track-html-coverage"
        )

        super().__init__(*args, **kwargs)
        self.loaded_html = True

    def get(self, url, *args, **kwargs):
        page = super().get(url, *args, **kwargs)
        self.loaded_html = False
        return page

    def find_element(self, *args, **kwargs):
        element = super().find_element(*args, **kwargs)
        if self.plugin:
            try:
                if not self.loaded_html:
                    self.plugin.cover(self.page_source)
                self.plugin.called_find_element(element)
            except selenium.common.exceptions.StaleElementReferenceException:
                pass
        self.loaded_html = True
        return element
