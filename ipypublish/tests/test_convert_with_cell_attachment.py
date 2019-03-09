import pytest


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('nb_with_attachment')
def test_basic_pdf(ipynb_app):
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True}})
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
    ipynb_app.assert_converted_equals_expected("latex_ipypublish_main")
