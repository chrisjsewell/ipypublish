import pytest


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('nb_complex_outputs')
def test_complex_latex(ipynb_app):
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
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True},
        "default_ppconfig_kwargs":  {"pdf_debug": True}})

    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
    ipynb_app.assert_converted_equals_expected("latex_ipypublish_main")


@pytest.mark.ipynb('nb_complex_outputs')
def test_complex_html(ipynb_app):
    """ includes:

    - internal (image) files
    - external logo and bib

    """
    ipynb_app.run({
        "conversion": "html_ipypublish_main"})

    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_equals_expected("html_ipypublish_main")


@pytest.mark.ipynb('nb_complex_outputs')
def test_complex_slides(ipynb_app):
    """ includes:

    - internal (image) files
    - external logo and bib

    """
    ipynb_app.run({
        "conversion": "slides_ipypublish_main",
        "default_pporder_kwargs": {"slides": True}})

    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_equals_expected("slides_ipypublish_main")


@pytest.mark.ipynb('nb_complex_outputs')
def test_complex_sphinx_rst(ipynb_app):
    """ includes:

    - internal (image) files
    - external logo and bib

    """
    if ipynb_app.pandoc_version < '2.6':
        raise AssertionError("pandoc version must be >= 2.6")

    ipynb_app.run({
        "conversion": "sphinx_ipypublish_all",
        "default_pporder_kwargs": {"slides": True}})

    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_equals_expected(
        "sphinx_ipypublish_all.pandoc.2-6")
