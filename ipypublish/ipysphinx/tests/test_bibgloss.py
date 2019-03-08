# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import re
import pytest

from ipypublish.ipysphinx.tests import get_test_source_dir


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss'))
def test_basic(app, status, warning, get_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_app_output(app, buildername='html')

    assert re.search(
        ('<a class="bibglossary reference internal" '
         'href="#term1" id="id1">name</a>'),
        output
    )
    assert re.search(
        ('<a class="bibglossary reference internal" '
         'href="#acro1" id="id2">OTHER</a>'),
        output)
    assert re.search(
        ('<tr><td class="label"><a.*'
         'href="\\#id2">\\[OTHER\\]</a></td><td>Abbrev of other</td></tr>'),
        output
    )
    assert re.search(
        ('<tr><td class="label"><a.*'
         'href="\\#id1">\\[name\\]</a></td><td>the description</td></tr>'),
        output
    )


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_missingref'))
def test_missingref(app, status, warning, get_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert "could not relabel bibglossary reference [missingkey]" in warnings

    # output = get_app_output(app, buildername='html')
