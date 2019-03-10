"""in this pytest conftest file we define an ipypublish test app fixture

This fixture supplies a configurable IpubTestApp, that can
run IPyPubMain on a specified source folder,
in a temporary folder (which will be deleted on teardown),
and has methods to test the output.

Usage:

.. code-block:: python

    @pytest.mark.ipynb('folder_name')
    def test_example(ipynb_app):
        ipynb_app.run({"conversion": "latex_ipypublish_main"})
        ipynb_app.assert_converted_exists()
        ipynb_app.assert_converted_contains(["regex1", "regex2"])
        ipynb_app.assert_converted_equals_expected("file_name")

@pytest.mark.ipynb accepts the key-word arguments:

- root: the root folder containing the test folders
  (default = ipypublish.tests.TEST_FILES_DIR))
- source: the folder name within <root>/<folder_name>
  that contains the source files (default = 'source')
- main_file: the file within <root>/<folder_name>/<source> to be converted
  (default = 'main.ipynb'). If None is given the source folder is used.
- converted: the folder name to output converted files to,
  either in the temporary folder (if out_to_temp=True) or
  <root>/<folder_name>/<converted> (if out_to_temp=False)
  (default = 'converted')
- expected: the folder name within <root>/<folder_name>
  that contains the expected output files (default = 'expected')
- out_to_temp: if True, converted files output to a temporary folder,
  that will be removed on teardown,
  otherwise output to <root>/<folder_name>/<converted> (will not be removed)
  (default=True)

"""
from collections import namedtuple
import copy
from difflib import context_diff
import io
import logging
import os
import shutil
import re
import tempfile

from nbconvert.utils.pandoc import get_pandoc_version
import pytest

from ipypublish.utils import pathlib
from ipypublish.tests import TEST_FILES_DIR
from ipypublish.convert.main import IpyPubMain

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def dont_open_webbrowser(monkeypatch):
    def nullfunc(*arg, **kwrgs):
        pass
    monkeypatch.setattr('webbrowser.open', nullfunc)


@pytest.fixture
def external_export_plugin():
    return pathlib.Path(os.path.join(TEST_FILES_DIR,
                                     'example_new_plugin.json'))


@pytest.fixture
def temp_folder():
    out_folder = tempfile.mkdtemp()
    yield out_folder
    shutil.rmtree(out_folder)


@pytest.fixture
def ipynb_params(request):
    """
    parameters that is specified by '@pytest.mark.ipynb'
    for ipynb conversion tests
    """

    # ##### process pytest.mark.ipynb

    if hasattr(request.node, 'iter_markers'):  # pytest-3.6.0 or newer
        markers = request.node.iter_markers("ipynb")
    else:
        markers = request.node.get_marker("ipynb")
    pargs = {}
    kwargs = {}

    if markers is not None:
        # to avoid stacking positional args
        for info in reversed(list(markers)):
            for i, a in enumerate(info.args):
                pargs[i] = a
            kwargs.update(info.kwargs)

    args = [pargs[i] for i in sorted(pargs.keys())]

    return namedtuple(
        'ipynb_params', 'args,kwargs')(args, kwargs)  # type: ignore


@pytest.fixture(scope='function')
def ipynb_app(temp_folder, ipynb_params):

    args, kwargs = ipynb_params
    if len(args) <= 0:
        raise ValueError(
            'a subfolder must be supplied as the first argument to '
            '@pytest.mark.ipynb')

    subfolder = args[0]  # 'ipynb_with_glossary'
    input_file = kwargs.get('main_file', 'main.ipynb')
    test_files_dir = kwargs.get('root', TEST_FILES_DIR)
    source_folder = kwargs.get('source', 'source')
    convert_folder = kwargs.get('converted', 'converted')
    expected_folder = kwargs.get('expected', 'expected')
    use_temp = kwargs.get('out_to_temp', True)

    source_folder_path = os.path.join(
        test_files_dir, subfolder, source_folder)
    expected_folder_path = os.path.join(
        test_files_dir, subfolder, expected_folder)

    temp_source_path = os.path.join(temp_folder, source_folder)
    shutil.copytree(source_folder_path, temp_source_path)

    if use_temp:
        converted_path = os.path.join(temp_folder, convert_folder)
    else:
        converted_path = os.path.join(
            test_files_dir, subfolder, convert_folder)

    yield IpyTestApp(
        temp_source_path,
        input_file,
        converted_path,
        expected_folder_path,
    )


class IpyTestApp(object):

    def __init__(self, src_path, input_file, converted_path,
                 expected_folder_path):
        self._src_folder_path = src_path
        self._converted_folder_path = converted_path
        self._expected_folder_path = expected_folder_path
        self._input_file = input_file
        self._output_data = None

    @property
    def source_path(self):
        return pathlib.Path(self._src_folder_path)

    @property
    def input_file(self):
        if self._input_file is None:
            return None
        return self.source_path.joinpath(self._input_file)

    @property
    def converted_path(self):
        return pathlib.Path(self._converted_folder_path)

    @property
    def expected_path(self):
        return pathlib.Path(self._expected_folder_path)

    @property
    def pandoc_version(self):
        return get_pandoc_version()

    def run(self, ipub_config=None):
        if ipub_config is None:
            ipub_config = {}
        ipub_config["outpath"] = str(self.converted_path)
        app = IpyPubMain(
            config={"IpyPubMain": ipub_config})
        self._output_data = app(self.input_file if self.input_file is not None
                                else self.source_path)

    @property
    def output_data(self):
        if self._output_data is None:
            raise ValueError(
                "the app must be run first to retrieve output data")
        return copy.copy(self._output_data)

    @property
    def export_extension(self):
        if self._output_data is None:
            raise ValueError(
                "the app must be run first to retrieve export file extension")
        exporter = self._output_data["exporter"]
        return exporter.file_extension

    @property
    def export_mimetype(self):
        if self._output_data is None:
            raise ValueError(
                "the app must be run first to retrieve export mimetype")
        exporter = self._output_data["exporter"]
        return exporter.output_mimetype

    def assert_converted_exists(self, file_name=None, extension=None):
        if file_name is None:
            if self.input_file is None:
                file_name = self.source_path.name
            else:
                file_name = os.path.splitext(self.input_file.name)[0]
        if extension is None:
            extension = self.export_extension

        converted_path = self.converted_path.joinpath(file_name + extension)
        if not self.converted_path.joinpath(file_name + extension).exists():
            raise AssertionError("could not find: {}".format(converted_path))

    def assert_converted_contains(self, regexes, encoding='utf8'):

        if self.input_file is None:
            file_name = self.source_path.name
        else:
            file_name = os.path.splitext(self.input_file.name)[0]
        extension = self.export_extension
        converted_path = self.converted_path.joinpath(file_name + extension)

        with io.open(str(converted_path), encoding=encoding) as fobj:
            content = fobj.read()

        if not isinstance(regexes, (list, tuple)):
            regexes = [regexes]

        for regex in regexes:

            if not re.search(regex, content):
                raise AssertionError(
                    "content does not contain regex: {}".format(regex))

    def assert_converted_equals_expected(self, expected_file_name,
                                         encoding='utf8'):

        if self.input_file is None:
            file_name = self.source_path.name
        else:
            file_name = os.path.splitext(self.input_file.name)[0]
        extension = self.export_extension
        converted_path = self.converted_path.joinpath(file_name + extension)

        expected_path = self.expected_path.joinpath(
            expected_file_name + extension)

        mime_type = self.export_mimetype
        if mime_type == 'text/latex':
            compare_tex_files(
                converted_path, expected_path, encoding=encoding)
        elif mime_type == 'text/html':
            compare_html_files(
                converted_path, expected_path, encoding=encoding)
        elif mime_type == 'text/restructuredtext':
            compare_rst_files(
                converted_path, expected_path, encoding=encoding)
        else:
            # TODO add comparison for nb (applicatio/json)
            # and python (application/x-python)
            message = ("no comparison function exists for "
                       "mimetype: {}".format(mime_type))
            # raise ValueError(message)
            logger.warn(message)


def compare_rst_files(testpath, outpath, encoding='utf8'):
    # only compare body of html, since styles differ by
    # nbconvert/pandoc version (e.g. different versions of font-awesome)

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding=encoding) as fobj:
            content = fobj.read()

        # python 3.5 used .jpg instead of .jpeg
        content = content.replace(".jpg", ".jpeg")

        output.append(content)

    test_content, out_content = output

    # only report differences
    if out_content != test_content:
        raise AssertionError("\n"+"\n".join(context_diff(
            test_content.splitlines(), out_content.splitlines(),
            fromfile=str(testpath), tofile=str(outpath))))


def compare_html_files(testpath, outpath, encoding='utf8'):
    # only compare body of html, since styles differ by
    # nbconvert/pandoc version (e.g. different versions of font-awesome)

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding=encoding) as fobj:
            content = fobj.read()

        # extract only the body
        # could use html.parser or beautifulsoup to do this better
        body_rgx = re.compile("\\<body\\>(.*)\\</body\\>", re.DOTALL)
        body_search = body_rgx.search(content)
        if not body_search:
            raise IOError("could not find body content of {}".format(path))
        content = body_search.group(1)

        # remove script environments which can change (e.g. reveal)
        script_rgx = re.compile("\\<script\\>(.*)\\</script\\>", re.DOTALL)
        content = script_rgx.sub("<script></script>", content)

        # remove trailing whitespace
        content = "\n".join([l.rstrip() for l in content.splitlines()])

        output.append(content)

    test_content, out_content = output

    # only report differences
    if out_content != test_content:
        raise AssertionError("\n"+"\n".join(context_diff(
            test_content.splitlines(), out_content.splitlines(),
            fromfile=str(testpath), tofile=str(outpath))))


def compare_tex_files(testpath, outpath, encoding='utf8'):

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding=encoding) as fobj:
            content = fobj.read()

        # only certain versions of pandoc wrap sections with \hypertarget
        # NOTE a better way to do this might be to use TexSoup
        ht_rgx = re.compile("\\\\hypertarget\\{[^\\}]*\\}\\{[^\\\\]*"
                            "(\\\\[sub]*section\\{[^\\}]*\\}"
                            "\\\\label\\{[^\\}]*\\})"
                            "\\}",
                            re.DOTALL)
        content = ht_rgx.sub("\\g<1>", content)

        # newer versions of pandoc convert ![](file) to \begin{figure}[htbp]
        # TODO override pandoc figure placement of ![](file) in markdown2latex
        content = content.replace("\\begin{figure}[htbp]", "\\begin{figure}")

        # at start of itemize
        content = content.replace("\\itemsep1pt\\parskip0pt\\parsep0pt\n", "")
        # at start of enumerate
        content = content.replace("\\tightlist\n", "")

        # python 3.5 used .jpg instead of .jpeg
        content = content.replace(".jpg", ".jpeg")

        # python < 3.6 sorts these differently
        pyg_rgx = re.compile(
            ("\\\\expandafter\\\\def\\\\csname "
                "PY\\@tok\\@[0-9a-zA-Z]*\\\\endcsname[^\n]*"),
            re.MULTILINE)
        content = pyg_rgx.sub(r"\<pygments definition\>", content)

        # also remove all space from start of lines
        space_rgx = re.compile(r"^[\s]*", re.MULTILINE)
        content = space_rgx.sub("", content)

        # remove trailing whitespace
        content = "\n".join([l.rstrip() for l in content.splitlines()])

        output.append(content)

    test_content, out_content = output

    # only report differences
    if out_content != test_content:
        raise AssertionError("\n"+"\n".join(context_diff(
            test_content.splitlines(), out_content.splitlines(),
            fromfile=str(testpath), tofile=str(outpath))))
