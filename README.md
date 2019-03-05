Pytest plugin for test reporting
================================

Offers additional reporting options for tests status.


To execute it:

    $ pytest demo --track term
    =========================================================================================== test session starts ============================================================================================
    plugins: track-0.1.0
    collected 7 items

    demo/test_models.py .s.s.                                                                                                                                                                            [ 71%]
    demo/test_views.py .s                                                                                                                                                                                [100%]

    =================================================================================== 4 passed, 3 skipped in 0.02 seconds ====================================================================================
    Total: 4 from 7 tests not skipped (57.14%)
        test_models, 3 from 5 tests not skipped (60.00%)
        test_views, 1 from 2 tests not skipped (50.00%)


Features
--------

Current functionality requires only test collection so this can be used with pytest's `--collect-only`


### Confluence reporting

To configure Confluence settings add a section to pytest.ini

    [pytest_track]
    confluence_username=<confluence_username>
    confluence_password=<confluence_password>
    confluence_url=<confluence_root_url>
    confluence_parent_page_id=<id_of_the_parent_page>
    confluence_page_title=<title_for_the_results_page>

To use it

    pytest demo --track confluence


Acknowledgements
----------------

Based on the initial work of Vasilica Dumbrava.
