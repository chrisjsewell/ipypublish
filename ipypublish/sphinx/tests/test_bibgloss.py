# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import re
import sys
import pytest

from ipypublish.sphinx.tests import get_test_source_dir


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_basic'))
def test_basic(app, status, warning, get_sphinx_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername='html')

    assert re.search(
        ('<a class="bibglossary bibgcapital reference internal" '
         'href="#term1" id="id1">Name</a>'),
        output
    )
    assert re.search(
        ('<a class="bibglossary reference internal" '
         'href="#term2" id="id2">name2</a>'),
        output
    )
    assert re.search(
        ('<a class="bibglossary reference internal" '
         'href="#acro1" id="id3">OTHER</a>'),
        output)

    assert re.search(
        ('<a class="bibglossary bibgplural bibgcapital reference internal" '
         'href="#term1" id="id4">Names</a>'),
        output
    )
    assert re.search(
        ('<a class="bibglossary bibgplural reference internal" '
         'href="#term2" id="id5">name2 plural</a>'),
        output
    )

    assert re.search(
        ('<tr><td class="label">\\[name\\].*'
         'href="\\#id1".*'
         'href="\\#id4".*'
         'the description which '
         'contains latex <span class="[^\\"]*math[^\\"]*">'
         '\\\\\\(\\\\frac\\{-23\\}\\{129\\}\\\\\\)'
         '</span></td></tr>'),
        output
    )
    assert re.search(
        ('<tr><td class="label">\\[name2\\].*'
         'href="\\#id2".*'
         'href="\\#id5".*'
         'the description which contains</p>'),
        output
    )
    assert re.search(
        ('<tr><td class="label"><a.*'
         'href="\\#id3">\\[OTHER\\]</a></td><td>Abbrev of other</td></tr>'),
        output
    )

    assert re.search(
        (
            '<tr><td class="label">.*\\[name\\].*'
            '<tr><td class="label">.*\\[name2\\].*'
            '<tr><td class="label">.*\\[OTHER\\].*'
        ),
        output,
        re.DOTALL
    )


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_sortkeys'))
def test_sortkeys(app, status, warning, get_sphinx_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername='html')

    assert re.search(
        (
            '<tr><td class="label">.*href="\\#id1">\\[name\\].*'
            '<tr><td class="label">.*href="\\#id3">.*pi.*'
            '<tr><td class="label">.*href="\\#id2">\\[MA\\].*'
        ),
        output,
        re.DOTALL
    )


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_unsorted'))
def test_unsorted(app, status, warning, get_sphinx_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername='html')

    assert re.search(
        (
            '<tr><td class="label">.*href="\\#id1">\\[name\\].*'
            '<tr><td class="label">.*href="\\#id2">\\[OTHER\\].*'
            '<tr><td class="label">.*href="\\#id3">\\[name2\\].*'
        ),
        output,
        re.DOTALL
    )


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_missingref'))
def test_missingref(app, status, warning, get_sphinx_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert "could not relabel bibglossary reference [missingkey]" in warnings


@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_duplicatekey'))
def test_duplicatekey(app, status, warning, get_sphinx_app_output):

    with pytest.raises(KeyError):
        app.build()


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
@pytest.mark.sphinx(
    buildername='html',
    srcdir=get_test_source_dir('bibgloss_tex'))
def test_load_tex(app, status, warning, get_sphinx_app_output):

    app.build()

    assert 'build succeeded' in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""
