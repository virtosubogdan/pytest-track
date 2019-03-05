from html import escape

from atlassian import Confluence

from .models import Module


def make_table(rows):
    # TODO: use templating
    table = "<table><tbody><tr><th>Name</th><th>Status (OK/Total)</th><th>Status (%)</th></tr>"
    for name, status, prc_status in rows:
        table += (
            '<tr><td><pre>{}</pre></td><td style="text-align: right;">{}</td>'
            '<td style="text-align: right;">{:.2f}%</td></tr>'
        ).format(name, status, prc_status)
    table += "</tbody></table>"
    return table


def make_report_rows(module, indent=0):
    rows = []
    for (item_name, value) in module.modules.items():
        if isinstance(value, Module):
            ok, total, prc_ok = value.stats
            name = " " * indent + escape(item_name.split("::")[-1])
            rows.append((name, "{}/{}".format(ok, total), prc_ok))
            rows.extend(make_report_rows(value, indent + 4))
    return rows


def report_to_confluence(report, config):
    track_config = config.inicfg.config.sections["pytest_track"]
    api = Confluence(
        url=track_config["confluence_url"],
        username=track_config["confluence_username"],
        password=track_config["confluence_password"],
    )
    parent_id = track_config["confluence_parent_page_id"]
    rows = make_report_rows(report.tests)
    body = "<p>{}</p>".format(make_table(rows))
    page_title = track_config["confluence_page_title"]
    response = api.update_or_create(parent_id, page_title, body=body)
    links = response['_links']
    page_url = '{}{}'.format(links['base'], links['webui'])
    print('Page available at {}'.format(page_url))