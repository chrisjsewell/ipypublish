# -*- coding: utf-8 -*-
"""
    test_sphinx
    ~~~~~~~~~~~

    General Sphinx test and check output.
"""
import re
from textwrap import dedent
import pytest


@pytest.mark.parametrize('sphinx_app', ['notebook'], indirect=True)
def test_sphinx(sphinx_app):
    sphinx_app.get_app().builder.build_all()
    assert sphinx_app.run_warnings == ""
    output = sphinx_app.output_text
    
    assert re.search(
        dedent("""\
        <pre>

        This is some printed text,
        with a nicely formatted output\\.

        </pre>"""),
        output
    )
