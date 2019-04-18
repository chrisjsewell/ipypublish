import pytest


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('nb_with_bib')
def test_withbib_latex(ipynb_app):
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True}})
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
    ipynb_app.assert_converted_contains([
        r"\\cite\{zelenyak_molecular_2016\}",
        r"\\bibliographystyle\{unsrtnat\}",
        r"\\bibliography\{main_files/test\}"
    ])


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('nb_with_glossary_tex', out_to_temp=True)
def test_withglossary_tex_latex(ipynb_app):
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True}})
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
    ipynb_app.assert_converted_contains([
        r"\\makeglossaries",
        r"\\gls\{term1\}",
        r"\\printglossary"
    ])


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('nb_with_glossary_bib', out_to_temp=True)
def test_withglossary_bib_latex(ipynb_app):
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True}})
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
    ipynb_app.assert_converted_contains([
        r"\\makeglossaries",
        r"\\gls\{term1\}",
        r"\\printglossary"
    ])
