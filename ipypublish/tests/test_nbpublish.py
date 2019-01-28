import os
import re
import io
from difflib import context_diff

import pytest

from ipypublish.main import publish
from ipypublish.scripts import pdfexport
from ipypublish.main import iter_all_plugin_paths
from ipypublish.tests import TEST_FILES_DIR


def test_pdf_export(temp_folder):

    tex_content = """
\\documentclass{article}
\\begin{document}
hallo world
\\end{document}
"""

    tex_path = os.path.join(temp_folder, 'test.tex')
    pdf_path = os.path.join(temp_folder, 'test.pdf')

    with open(tex_path, 'w') as f:
        f.write(tex_content)
    pdfexport.export_pdf(tex_path, temp_folder)
    assert os.path.exists(pdf_path)


def test_publish_ipynb1_latex(temp_folder, ipynb1):

    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb1.name)[0] + '.tex')

    publish(ipynb1, outpath=temp_folder)
    assert os.path.exists(tex_path)


def test_publish_folder1_latex(ipynb_folder):

    tex_path = os.path.join(ipynb_folder,
                            os.path.basename(ipynb_folder) + '.tex')

    publish(ipynb_folder, outpath=ipynb_folder)
    assert os.path.exists(tex_path)


@pytest.mark.requires_latexmk
def test_publish_ipynb1_pdf(temp_folder, ipynb1):

    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb1.name)[0] + '.tex')
    pdf_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb1.name)[0] + '.pdf')

    publish(ipynb1, outpath=temp_folder, create_pdf=True)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)


@pytest.mark.requires_latexmk
def test_publish_withbib(temp_folder, ipynb_with_bib):
    tex_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb_with_bib.name)[0] + '.tex')
    pdf_path = os.path.join(temp_folder,
                            os.path.splitext(ipynb_with_bib.name)[0] + '.pdf')

    publish(ipynb_with_bib, outpath=temp_folder, create_pdf=True)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)


@pytest.mark.requires_latexmk
def test_publish_with_external(ipynb_folder_with_external, tex_with_external):
    """ includes:

    - international language (portugese)
    - non-ascii characters in text
    - internal (image) files
    - external logo and bib

    """
    basename = os.path.basename(ipynb_folder_with_external)
    tex_path = os.path.join(ipynb_folder_with_external,
                            basename + '.tex')
    pdf_path = os.path.join(ipynb_folder_with_external,
                            basename + '.pdf')
    publish(ipynb_folder_with_external,
            conversion='latex_ipypublish_main',
            outpath=ipynb_folder_with_external,
            create_pdf=True, pdf_debug=True)
    assert os.path.exists(tex_path)
    assert os.path.exists(pdf_path)
    compare_tex_files(tex_with_external, tex_path)


def test_publish_ipynb1_html(temp_folder, ipynb1):

    html_path = os.path.join(temp_folder,
                             os.path.splitext(ipynb1.name)[0] + '.html')

    publish(ipynb1, conversion='html_ipypublish_main', outpath=temp_folder)
    assert os.path.exists(html_path)


def test_publish_ipynb1_slides(temp_folder, ipynb1):

    html_path = os.path.join(temp_folder, os.path.splitext(
        ipynb1.name)[0] + '.slides.html')

    publish(ipynb1, conversion='slides_ipypublish_main',
            outpath=temp_folder)
    assert os.path.exists(html_path)


@pytest.mark.parametrize(
    "plugin_name,plugin_path",
    list(iter_all_plugin_paths())
)
def test_publish_run_all_plugins(temp_folder, ipynb1,
                                 plugin_name, plugin_path):

    outpath, exporter = publish(
        ipynb1, conversion=plugin_name, outpath=temp_folder)
    outname = os.path.splitext(ipynb1.name)[0] + exporter.file_extension
    outfile = os.path.join(temp_folder, outname)
    testfile = os.path.join(TEST_FILES_DIR, "ipynb1_converted",
                            plugin_name + exporter.file_extension)
    assert os.path.exists(outfile), "could not find: {} for {}".format(
        outfile, plugin_name)
    assert os.path.exists(testfile), "could not find: {} for {}".format(
        testfile, plugin_name)

    # only compare latex files, since html has styles differing by
    # nbconvert version (e.g. different versions of font-awesome)
    if exporter.output_mimetype == 'text/latex':

        compare_tex_files(testfile, outfile)

    # TODO for html, use html.parser or beautifulsoup to compare only body


def compare_tex_files(testpath, outpath):

    output = []
    for path in [testpath, outpath]:

        with io.open(str(path), encoding='utf8') as fobj:
            content = fobj.read()

        # only certain versions of pandoc wrap sections with \hypertarget
        # NOTE a better way to do this might be to use TexSoup
        ht_rgx = re.compile("\\\\hypertarget\\{.*\\}\\{[^\\\\]*(.*\\})\\}",
                            re.DOTALL)
        content = ht_rgx.sub("\\g<1>", content)

        # python < 3.6 sorts these differently
        pyg_rgx = re.compile(
            ("\\\\expandafter\\\\def\\\\csname "
                "PY\\@tok\\@[0-9a-zA-Z]*\\\\endcsname[^\n]*"),
            re.MULTILINE)
        content = pyg_rgx.sub("\<pygments definition\>", content)

        # also remove all space from start of lines
        space_rgx = re.compile("^[\s]*", re.MULTILINE)
        content = space_rgx.sub("", content)
        output.append(content)

    test_content, out_content = output

    # only report differences
    if out_content != test_content:
        raise AssertionError("\n"+"\n".join(context_diff(
            test_content.splitlines(), out_content.splitlines(),
            fromfile=str(testpath), tofile=str(outpath))))
