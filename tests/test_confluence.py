from pytest_track.confluence import make_table, make_report_rows


def test_table_making():
    rows = [(1, 2, 3)]
    expected = (
        "<table><tbody><tr><th>Name</th><th>Status (OK/Total)</th><th>Status (%)</th></tr>"
        '<tr><td><pre>1</pre></td><td style="text-align: right;">2</td>'
        '<td style="text-align: right;">3.00%</td></tr></tbody></table>'
    )
    assert make_table(rows) == expected


def test_make_rows(simple_module):
    expected_rows = [("test_module", "1/2", 50.0)]
    assert make_report_rows(simple_module) == expected_rows


def test_report():
    pass
