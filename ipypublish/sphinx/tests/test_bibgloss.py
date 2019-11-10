# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import sys
import pytest
import sphinx

from ipypublish.sphinx.tests import get_test_source_dir

from ipypublish.tests.utils import HTML2JSONParser


@pytest.mark.sphinx(buildername="html", srcdir=get_test_source_dir("bibgloss_basic"))
def test_basic(app, status, warning, get_sphinx_app_output, data_regression):

    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername="html")

    parser = HTML2JSONParser()
    parser.feed(output)
    if sphinx.version_info >= (2,):
        data_regression.check(parser.parsed, basename="test_basic_v2")
    else:
        data_regression.check(parser.parsed, basename="test_basic_v1")


@pytest.mark.sphinx(buildername="html", srcdir=get_test_source_dir("bibgloss_sortkeys"))
def test_sortkeys(app, status, warning, get_sphinx_app_output, data_regression):

    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername="html")

    parser = HTML2JSONParser()
    parser.feed(output)
    if sphinx.version_info >= (2,):
        data_regression.check(parser.parsed, basename="test_sortkeys_v2")
    else:
        data_regression.check(parser.parsed, basename="test_sortkeys_v1")


@pytest.mark.sphinx(buildername="html", srcdir=get_test_source_dir("bibgloss_unsorted"))
def test_unsorted(app, status, warning, get_sphinx_app_output, data_regression):

    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""

    output = get_sphinx_app_output(app, buildername="html")

    parser = HTML2JSONParser()
    parser.feed(output)
    if sphinx.version_info >= (2,):
        data_regression.check(parser.parsed, basename="test_unsorted_v2")
    else:
        data_regression.check(parser.parsed, basename="test_unsorted_v1")


@pytest.mark.sphinx(
    buildername="html", srcdir=get_test_source_dir("bibgloss_missingref")
)
def test_missingref(app, status, warning, get_sphinx_app_output):

    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    if (
        "could not relabel bibglossary reference [missingkey]" not in warnings
        and "WARNING: citation not found: missingkey" not in warnings  # sphinx < 2
    ):  # sphinx >= 2
        raise AssertionError(
            "should raise warning for missing citation `missingkey`: {}".format(
                warnings
            )
        )


@pytest.mark.sphinx(
    buildername="html", srcdir=get_test_source_dir("bibgloss_duplicatekey")
)
def test_duplicatekey(app, status, warning, get_sphinx_app_output):

    with pytest.raises(KeyError):
        app.build()


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135",
)
@pytest.mark.sphinx(buildername="html", srcdir=get_test_source_dir("bibgloss_tex"))
def test_load_tex(app, status, warning, get_sphinx_app_output):

    app.build()

    assert "build succeeded" in status.getvalue()  # Build succeeded
    warnings = warning.getvalue().strip()
    assert warnings == ""
