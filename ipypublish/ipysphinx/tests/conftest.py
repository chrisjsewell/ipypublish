import os
import shutil
import tempfile

import pytest
from six import StringIO

import sphinx
from sphinx.application import Sphinx
from sphinx import __version__ as sphinx_version

from ipypublish.ipysphinx.tests import TESTDIR

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


@pytest.fixture
def sphinx_app():
    srcdir = pathlib.Path(TESTDIR)
    if srcdir.joinpath('_build').exists():
        shutil.rmtree(str(srcdir.joinpath('_build')),
                      ignore_errors=True, onerror=None)
    status = StringIO()
    warning = StringIO()
    app = None
    exc = None
    try:
        app = TestApp(srcdir=srcdir, status=status, warning=warning,
                      # outdir=srcdir.parent.joinpath("_build")
                      )
        yield app, status, warning
    except Exception as _exc:
        exc = _exc
        raise
    finally:
        if app:
            if exc:
                app.cleanup(error=exc)
            else:
                app.cleanup()


def mkdtemp(suffix='', prefix='tmp', dir=None):

    tmpdir = tempfile.mkdtemp(
        suffix, prefix, str(dir) if dir is not None else None)

    return pathlib.Path(tmpdir)


class TestApp(Sphinx):
    """
    A subclass of :class:`sphinx.application.Sphinx`,
    that runs on the test root,
    with some better default values for the initialization parameters.
    """

    def __init__(self, srcdir=None, confdir=None, outdir=None, doctreedir=None,
                 buildername='html', confoverrides=None, status=None,
                 warning=None, freshenv=False, warningiserror=False, tags=None,
                 copy_srcdir_to_tmpdir=False, create_new_srcdir=False,
                 cleanup_on_errors=True, verbosity=0, parallel=0):
        self.cleanup_trees = []
        self.cleanup_on_errors = cleanup_on_errors

        if create_new_srcdir:
            assert srcdir is None, 'conflicted: create_new_srcdir, srcdir'
            tmpdir = mkdtemp()
            self.cleanup_trees.append(tmpdir)
            tmproot = tmpdir.joinpath('root')
            tmproot.mkdir()
            (tmproot / 'conf.py').write_text('')
            srcdir = tmproot

        assert srcdir is not None, 'srcdir not found'
        srcdir = pathlib.Path(srcdir).absolute()

        if copy_srcdir_to_tmpdir:
            tmpdir = mkdtemp()
            self.cleanup_trees.append(tmpdir)
            tmproot = tmpdir / srcdir.basename()
            srcdir.copytree(tmproot)
            srcdir = tmproot
            self.builddir = srcdir.joinpath('_build')
        else:
            self.builddir = mkdtemp()
            self.cleanup_trees.append(self.builddir)

        if confdir is None:
            confdir = srcdir
        if outdir is None:
            outdir = self.builddir.joinpath(buildername)
            if not outdir.is_dir():
                outdir.mkdir()
        if doctreedir is None:
            doctreedir = self.builddir.joinpath('doctrees')
            if not doctreedir.is_dir():
                doctreedir.mkdir()
        if confoverrides is None:
            confoverrides = {}
        if status is None:
            status = StringIO()
        if warning is None:
            warning = StringIO()

        try:
            sphinx.application.abspath = lambda x: x
            if sphinx_version < '1.3':
                Sphinx.__init__(self, str(srcdir), confdir, outdir, doctreedir,
                                buildername, confoverrides, status,
                                warning, freshenv, warningiserror, tags)
            else:
                Sphinx.__init__(self, str(srcdir), confdir, outdir, doctreedir,
                                buildername, confoverrides, status,
                                warning, freshenv, warningiserror, tags,
                                verbosity, parallel)
        finally:
            sphinx.application.abspath = os.path.abspath

    def __repr__(self):
        classname = self.__class__.__name__
        return '<%s buildername=%r>' % (classname, self.builder.name)

    def cleanup(self, error=None):
        if error and self.cleanup_on_errors is False:
            return

        if sphinx_version < '1.6':
            from sphinx.theming import Theme
            Theme.themes.clear()

        try:
            from sphinx.ext.autodoc import AutoDirective
            AutoDirective._registry.clear()
        except ImportError:
            pass  # Sphinx-2.0+ does not have AutoDirective and its cache

        for tree in self.cleanup_trees:
            shutil.rmtree(tree, True)
