import pytest


@pytest.mark.ipynb('basic_nb')
def test_basic_latex(ipynb_app):
    ipynb_app.run({"conversion": "latex_ipypublish_main"})
    ipynb_app.assert_converted_exists()


@pytest.mark.ipynb('basic_nb')
def test_basic_html(ipynb_app):
    ipynb_app.run({"conversion": "html_ipypublish_main"})
    ipynb_app.assert_converted_exists()


@pytest.mark.ipynb('basic_nb')
def test_basic_slides(ipynb_app):
    ipynb_app.run({
        "conversion": "slides_ipypublish_main",
        "default_pporder_kwargs": {"slides": True}
        })
    ipynb_app.assert_converted_exists()


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('basic_nb')
def test_basic_pdf(ipynb_app):
    ipynb_app.run({
        "conversion": "latex_ipypublish_main",
        "default_pporder_kwargs": {"create_pdf": True}})
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
