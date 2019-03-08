# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import re
import pytest


def test_sphinx(sphinx_app):
    app, status, warning = sphinx_app
    app.builder.build_all()
    warnings = warning.getvalue()
    assert warnings == ""
    output = (app.outdir / "contents.html").read_text(encoding='utf-8')

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
