import os
import re
import io
import sys
from difflib import context_diff

import pytest

from ipypublish.convert.main import IpyPubMain
from ipypublish.convert.config_manager import iter_all_export_paths
from ipypublish.tests import TEST_FILES_DIR


def test_publish_ipynb1_latex(temp_folder, ipynb1):

    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb1.name)[0] + '.tex')

    IpyPubMain(config={"IpyPubMain": {"outpath": temp_folder}})(ipynb1)
    assert os.path.exists(tex_path)


def test_publish_folder1_latex(ipynb_folder):

    tex_path = os.path.join(ipynb_folder,
                            os.path.basename(ipynb_folder) + '.tex')

    IpyPubMain(config={"IpyPubMain": {"outpath": ipynb_folder}})(ipynb_folder)
    assert os.path.exists(tex_path)


@pytest.mark.requires_latexmk
def test_publish_ipynb1_pdf(temp_folder, ipynb1):

    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb1.name)[0] + '.tex')
    pdf_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb1.name)[0] + '.pdf')

    IpyPubMain(config={"IpyPubMain":
                       {"outpath": temp_folder,
                        "default_pporder_kwargs": {"create_pdf": True}}},
               )(ipynb1)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)


@pytest.mark.requires_latexmk
def test_publish_markdown_cells_latex(temp_folder, nb_markdown_cells):
    """ test notebook containing attachments

    """
    ipynb = nb_markdown_cells["input_file"]
    tex_file = nb_markdown_cells["latex_ipypublish_main"]

    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb.name)[0] + '.tex')
    pdf_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb.name)[0] + '.pdf')

    IpyPubMain(config={"IpyPubMain":
                       {"outpath": temp_folder,
                        "conversion": "latex_ipypublish_main",
                        "default_pporder_kwargs": {"create_pdf": True}}}
               )(ipynb)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)
    compare_tex_files(tex_file, tex_path)


def test_publish_markdown_cells_rst(temp_folder, nb_markdown_cells):
    """ test notebook containing attachments

    """
    ipynb = nb_markdown_cells["input_file"]
    rst_file = nb_markdown_cells["sphinx_ipypublish_main"]

    rst_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb.name)[0] + '.rst')

    IpyPubMain(config={"IpyPubMain": {
        "outpath": temp_folder,
        "conversion": "sphinx_ipypublish_main"}}
    )(ipynb)
    assert os.path.exists(rst_path)
    compare_rst_files(rst_file, rst_path)


@pytest.mark.requires_latexmk
def test_publish_withbib(temp_folder, ipynb_with_bib):
    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb_with_bib.name)[0] + '.tex')
    pdf_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb_with_bib.name)[0] + '.pdf')

    IpyPubMain(config={"IpyPubMain": {
        "outpath": temp_folder,
        "default_pporder_kwargs": {"create_pdf": True}}}
    )(ipynb_with_bib)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)


@pytest.mark.requires_latexmk
def test_publish_complex_latex(ipynb_folder_with_external):
    """ includes:

    - international language (portugese)
    - internal (image) files
    - external logo and bib

    TODO non-ascii characters in text not working on Linux
    This works locally (on osx) and on travis osx, but not for linux
    latexmk raises `Package utf8x Error: MalformedUTF-8sequence.` or
    `character used is undefined`
    presumable this is due to the way the ipynb is being encoded on osx

    """
    input_folder = ipynb_folder_with_external["input_folder"]
    expected = ipynb_folder_with_external["latex_ipypublish_main"]

    basename = os.path.basename(input_folder)
    tex_path = os.path.join(input_folder,
                            basename + '.tex')
    pdf_path = os.path.join(input_folder,
                            basename + '.pdf')
    IpyPubMain(config={"IpyPubMain":
                       {"outpath": input_folder,
                        "conversion": "latex_ipypublish_main",
                        "default_pporder_kwargs": {"create_pdf": True},
                        "default_ppconfig_kwargs":  {"pdf_debug": True}}}
               )(input_folder)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)
    compare_tex_files(expected, tex_path)


def test_publish_complex_html(ipynb_folder_with_external):
    """ includes:

    - internal (image) files
    - external logo and bib

    """
    input_folder = ipynb_folder_with_external["input_folder"]
    expected = ipynb_folder_with_external["html_ipypublish_main"]

    basename = os.path.basename(input_folder)
    html_path = os.path.join(input_folder,
                             basename + '.html')
    IpyPubMain(config={"IpyPubMain": {"outpath": input_folder,
                                      "conversion": "html_ipypublish_main"}
                       })(input_folder)
    assert os.path.exists(html_path)
    compare_html_files(expected, html_path)


def test_publish_complex_slides(ipynb_folder_with_external):
    """ includes:

    - internal (image) files
    - external logo and bib

    """
    input_folder = ipynb_folder_with_external["input_folder"]
    expected = ipynb_folder_with_external["slides_ipypublish_main"]

    basename = os.path.basename(input_folder)
    html_path = os.path.join(input_folder,
                             basename + '.slides.html')
    IpyPubMain(config={"IpyPubMain":
                       {"outpath": input_folder,
                        "conversion": "slides_ipypublish_main",
                        "default_pporder_kwargs": {"slides": True}}
                       })(input_folder)
    assert os.path.exists(html_path)
    compare_html_files(expected, html_path)


def test_publish_complex_rst(ipynb_folder_with_external):
    """ includes:

    - internal (image) files
    - external logo and bib

    """
    input_folder = ipynb_folder_with_external["input_folder"]
    expected = ipynb_folder_with_external["sphinx_ipypublish_all"]

    basename = os.path.basename(input_folder)
    rst_path = os.path.join(input_folder,
                            basename + '.rst')

    IpyPubMain(config={"IpyPubMain": {"outpath": input_folder,
                                      "conversion": "sphinx_ipypublish_all"}
                       })(input_folder)
    assert os.path.exists(rst_path)
    compare_rst_files(expected, rst_path)


def test_publish_ipynb1_html(temp_folder, ipynb1):

    html_path = os.path.join(temp_folder,
                             os.path.splitext(ipynb1.name)[0] + '.html')

    IpyPubMain(config={"IpyPubMain": {"outpath": temp_folder,
                                      "conversion": "html_ipypublish_main"}
                       })(ipynb1)
    assert os.path.exists(html_path)


def test_publish_ipynb1_slides(temp_folder, ipynb1):

    html_path = os.path.join(temp_folder, os.path.splitext(
        ipynb1.name)[0] + '.slides.html')

    IpyPubMain(config={"IpyPubMain":
                       {"outpath": temp_folder,
                        "conversion": "slides_ipypublish_main",
                        "default_pporder_kwargs": {"slides": True}}
                       })(ipynb1)
    assert os.path.exists(html_path)


@pytest.mark.parametrize(
    "plugin_name,plugin_path",
    list(iter_all_export_paths())
)
def test_publish_run_all_plugins(temp_folder, ipynb1,
                                 plugin_name, plugin_path):

    if ((plugin_name in ["sphinx_ipypublish_all.ext"]
         or "exec" in plugin_name) and sys.version_info[0] < 3):
        # TODO this fails because the kernel is set as python3 in the notebook
        # could add a replacement variable e.g. ${pykernel}
        # and allow parsing of it to main.publish (default = "")
        return

    # TODO "sphinx_ipypublish_all.run" launches a webbrowser tab

    outdata = IpyPubMain(config={"IpyPubMain": {"outpath": temp_folder,
                                                "conversion": plugin_name}}
                         )(ipynb1)

    exporter = outdata["exporter"]

    outname = os.path.splitext(ipynb1.name)[0] + exporter.file_extension
    outfile = os.path.join(temp_folder, outname)
    testfile = os.path.join(TEST_FILES_DIR, "ipynb1_converted",
                            plugin_name + exporter.file_extension)

    if plugin_name in ["python_with_meta_stream", "sphinx_ipypublish_all.ext"]:
        return
    if plugin_name in [
            "sphinx_ipypublish_all.run", "sphinx_ipypublish_main.run"]:
        assert os.path.exists(os.path.join(
            temp_folder, "build", "html",
            os.path.splitext(ipynb1.name)[0] + ".html"))
        return

    assert os.path.exists(outfile), "could not find: {} for {}".format(
        outfile, plugin_name)
    assert os.path.exists(testfile), "could not find: {} for {}".format(
        testfile, plugin_name)

    if exporter.output_mimetype == 'text/latex':
        compare_tex_files(testfile, outfile)
    elif exporter.output_mimetype == 'text/html':
        compare_html_files(testfile, outfile)
    elif exporter.output_mimetype == 'text/restructuredtext':
        compare_rst_files(testfile, outfile)


def compare_rst_files(testpath, outpath):
    # only compare body of html, since styles differ by
    # nbconvert/pandoc version (e.g. different versions of font-awesome)

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding='utf8') as fobj:
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


def compare_html_files(testpath, outpath):
    # only compare body of html, since styles differ by
    # nbconvert/pandoc version (e.g. different versions of font-awesome)

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding='utf8') as fobj:
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


def compare_tex_files(testpath, outpath):

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding='utf8') as fobj:
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
