import os
import shutil
import tempfile
import pytest

from ipypublish.main import publish
from ipypublish.scripts import pdfexport
from ipypublish.main import iter_all_plugin_paths


def test_pdf_export():

    tex_content = """
\\documentclass{article}
\\begin{document}
hallo world
\\end{document}
"""
    out_folder = tempfile.mkdtemp()
    tex_path = os.path.join(out_folder, 'test.tex')
    pdf_path = os.path.join(out_folder, 'test.pdf')
    try:
        with open(tex_path, 'w') as f:
            f.write(tex_content)
        pdfexport.export_pdf(tex_path, out_folder)
        assert os.path.exists(pdf_path)
    finally:
        shutil.rmtree(out_folder)


def test_publish_ipynb1_latex(ipynb1):

    out_folder = tempfile.mkdtemp()
    tex_path = os.path.join(out_folder, '2test.tex')
    try:
        publish(ipynb1, outpath=out_folder)
        assert os.path.exists(tex_path)
    finally:
        shutil.rmtree(out_folder)


def test_publish_folder1_latex(directory):

    out_folder = tempfile.mkdtemp()
    tex_path = os.path.join(out_folder, 'dir1.tex')
    try:
        publish(directory, outpath=out_folder)
        assert os.path.exists(tex_path)
    finally:
        shutil.rmtree(out_folder)


def test_publish_ipynb1_pdf(ipynb1):

    out_folder = tempfile.mkdtemp()
    tex_path = os.path.join(out_folder, '2test.tex')
    pdf_path = os.path.join(out_folder, '2test.pdf')
    try:
        publish(ipynb1, outpath=out_folder, create_pdf=True)
        assert os.path.exists(tex_path)
        assert os.path.exists(pdf_path)
    finally:
        shutil.rmtree(out_folder)

# TODO test_publish_withbib
# def test_publish_withbib(ipynb_with_bib):
# out_folder = tempfile.mkdtemp()
#     tex_path = os.path.join(out_folder,'test_with_bib.tex')
#     pdf_path = os.path.join(out_folder,'test_with_bib.pdf')
#     with ipynb_with_bib.maketemp() as ipynb_with_bib_dir:
#
#         try:
#             publish(ipynb_with_bib_dir.name,outpath=out_folder,create_pdf=True)
#             assert os.path.exists(tex_path)
#             assert os.path.exists(pdf_path)
#         finally:
#             shutil.rmtree(out_folder)


def test_publish_ipynb1_html(ipynb1):

    out_folder = tempfile.mkdtemp()
    html_path = os.path.join(out_folder, '2test.html')
    try:
        publish(ipynb1, conversion='html_ipypublish_main', outpath=out_folder)
        assert os.path.exists(html_path)
    finally:
        shutil.rmtree(out_folder)


def test_publish_ipynb1_slides(ipynb1):

    out_folder = tempfile.mkdtemp()
    html_path = os.path.join(out_folder, '2test.slides.html')
    try:
        publish(ipynb1, conversion='slides_ipypublish_main',
                outpath=out_folder)
        assert os.path.exists(html_path)
    finally:
        shutil.rmtree(out_folder)


@pytest.mark.parametrize(
    "plugin_name,plugin_path",
    list(iter_all_plugin_paths())
)
def test_publish_run_all_plugins(ipynb1, plugin_name, plugin_path):

    # for plugin_name, plugin_path in iter_all_plugin_paths():
    out_folder = tempfile.mkdtemp()
    try:
        publish(ipynb1, conversion=plugin_name, outpath=out_folder)
        # TODO test against file hash
    finally:
        shutil.rmtree(out_folder)

# TODO files with internal files
# TODO files with external files