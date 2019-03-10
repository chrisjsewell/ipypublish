# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import re
from textwrap import dedent
import pytest

from ipypublish.sphinx.tests import get_test_source_dir


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('notebook'))
def test_basic(app, status, warning, get_sphinx_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername='html')

    assert re.search(
        dedent("""\
        <pre>

        This is some printed text,
        with a nicely formatted output\\.

        </pre>"""),
        output
    )
