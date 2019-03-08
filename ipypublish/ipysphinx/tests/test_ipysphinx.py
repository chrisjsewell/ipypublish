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
    # assert re.search(u'could not relabel citation \\[Test01\\]', warnings)
    # assert re.search(u'could not relabel citation \\[Test02\\]', warnings)
    # assert re.search(u'could not relabel citation \\[Wa04\\]', warnings)
    # assert re.search(
    #     u'could not relabel citation reference \\[Test01\\]',
    #     warnings)
    # assert re.search(
    #     u'could not relabel citation reference \\[Test02\\]',
    #     warnings)
    # assert re.search(
    #     u'could not relabel citation reference \\[Wa04\\]',
    #     warnings)
