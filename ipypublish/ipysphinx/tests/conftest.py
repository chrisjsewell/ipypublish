import io
import os
import shutil
import tempfile

import pytest
from six import StringIO

import sphinx
from sphinx.application import Sphinx
from sphinx import __version__ as sphinx_version

from ipypublish.ipysphinx.tests import get_test_source_dir

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


@pytest.fixture
def sphinx_app(request):
    app = TestApp(request.param)
    yield app
    app.cleanup()


def mkdtemp(suffix='', prefix='tmp', dir=None):

    tmpdir = tempfile.mkdtemp(
        suffix, prefix, str(dir) if dir is not None else None)

    return pathlib.Path(tmpdir)


class TestApp(object):
    """ setup for `sphinx.application.Sphinx`,
    that runs on the test root,
    with some better default values for the initialization parameters.
    """
    verbosity = 0
    parallel = 0
    buildername = 'html'

    def __init__(self, srcdir=None, confdir=None, outdir=None,
                 status=None, warning=None,
                 copy_srcdir_to_tmpdir=False,
                 cleanup_on_errors=True):

        self.cleanup_trees = []
        self.cleanup_on_errors = cleanup_on_errors

        if status is None:
            self._status = StringIO()
        else:
            self._status = status
        if warning is None:
            self._warnings = StringIO()
        else:
            self._warnings = warning
        self.init_error = None

        assert srcdir is not None, 'srcdir not found'
        if not os.path.isabs(srcdir):
            srcdir = get_test_source_dir(srcdir)
        self.srcdir = pathlib.Path(srcdir).absolute()

        if copy_srcdir_to_tmpdir:
            tmpdir = mkdtemp()
            self.cleanup_trees.append(tmpdir)
            tmproot = tmpdir.joinpath(srcdir.basename())
            self.srcdir.copytree(tmproot)
            self.srcdir = tmproot
            self.builddir = srcdir.joinpath('_build')
        else:
            self.builddir = mkdtemp()
            self.cleanup_trees.append(self.builddir)

        if confdir is None:
            self.confdir = srcdir
        else:
            self.confdir = confdir

        if outdir is None:
            self.outdir = self.builddir.joinpath(self.buildername)
            if not self.outdir.is_dir():
                self.outdir.mkdir()
        else:
            self.outdir = outdir

        self.doctreedir = self.builddir.joinpath('doctrees')
        if not self.doctreedir.is_dir():
            self.doctreedir.mkdir()

    def __repr__(self):
        classname = self.__class__.__name__
        return '<%s buildername=%r>' % (classname, self.buildername)

    def get_app(self, confoverrides=None,
                freshenv=True, warningiserror=False, tags=None):

        if confoverrides is None:
            confoverrides = {}
        self.init_error = None
        try:
            sphinx.application.abspath = lambda x: x
            if sphinx_version < '1.3':
                app = Sphinx(
                    str(self.srcdir), str(self.confdir), str(self.outdir),
                    str(self.doctreedir), self.buildername,
                    confoverrides, self._status, self._warnings,
                    freshenv, warningiserror, tags)
            else:
                app = Sphinx(
                    str(self.srcdir), str(self.confdir), str(self.outdir),
                    str(self.doctreedir), self.buildername,
                    confoverrides, self._status, self._warnings,
                    freshenv, warningiserror, tags,
                    self.verbosity, self.parallel)
        except Exception as err:
            self.init_error = err
        finally:
            sphinx.application.abspath = os.path.abspath

        if not self.init_error:
            return app

    @property
    def run_warnings(self):
        return self._warnings.getvalue()

    @property
    def run_status(self):
        return self._status.getvalue()

    @property
    def output_text(self):
        outfile = os.path.join(self.outdir, "contents.html")
        if not os.path.exists(outfile):
            raise IOError("no output file exists: {}".format(outfile))
        with io.open(outfile, encoding='utf-8') as fobj:
            return fobj.read()

    def cleanup(self):
        if self.init_error and self.cleanup_on_errors is False:
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
