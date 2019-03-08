"""
Uses sphinx's pytest fixture to run builds

usage:

.. code-block:: python

    from ipypublish.ipysphinx.tests import get_test_source_dir

    @pytest.mark.sphinx(
        buildername='html',
        srcdir=get_test_source_dir('notebook'))
    def test_basic(app, status, warning, get_app_output):

        app.build()

        assert 'build succeeded' in status.getvalue()  # Build succeeded
        warnings = warning.getvalue().strip()
        assert warnings == ""

        output = get_app_output(app, buildername='html')

parameters available to parse to ``@pytest.mark.sphinx``:

- buildername='html'
- srcdir=None
- testroot='root' (only used if srcdir not set)
- freshenv=False
- confoverrides=None
- status=None
- warning=None
- tags=None
- docutilsconf=None

"""
import os
import shutil

import pytest
from sphinx.testing.path import path

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from ipypublish.ipysphinx.tests import get_test_source_dir


# @pytest.fixture(scope='session', autouse=True)
# def remove_sphinx_projects(sphinx_test_tempdir):
#     # Remove any directory which appears to be a Sphinx project from
#     # the temporary directory area.
#     # See https://github.com/sphinx-doc/sphinx/issues/4040
#     roots_path = pathlib.Path(sphinx_test_tempdir)
#     for entry in roots_path.iterdir():
#         try:
#             if entry.is_dir() and pathlib.Path(entry, '_build').exists():
#                 shutil.rmtree(str(entry))
#         except PermissionError:
#             pass

@pytest.fixture(scope='session', autouse=True)
def remove_sphinx_builds():
    """ remove all build directories from the test folder
    """
    srcdirs = pathlib.Path(get_test_source_dir())
    for entry in srcdirs.iterdir():  # type: pathlib.Path
        if entry.is_dir() and entry.joinpath("_build").exists():
            shutil.rmtree(str(entry.joinpath("_build")))


@pytest.fixture
def get_app_output():
    def read(app, buildername='html',
             filename="contents.html", encoding='utf-8'):

        outpath = path(os.path.join(
            str(app.srcdir), '_build', buildername, filename))
        if not outpath.exists():
            raise IOError("no output file exists: {}".format(outpath))
        return outpath.text(encoding=encoding)
    return read
