# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import pytest

from ipypublish.sphinx.tests import get_test_source_dir

from ipypublish.tests.utils import HTML2JSONParser


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('notebook'))
def test_basic(app, status, warning, get_sphinx_app_output, data_regression):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername='html')

    parser = HTML2JSONParser()
    parser.feed(output)
    data_regression.check(parser.parsed)
