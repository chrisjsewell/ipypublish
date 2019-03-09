import pytest


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('nb_with_bib')
def test_withbib_latex(ipynb_app):
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True}})
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
