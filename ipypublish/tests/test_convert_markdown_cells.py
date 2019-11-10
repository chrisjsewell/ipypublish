import pytest


@pytest.mark.requires_latexmk
@pytest.mark.ipynb("nb_markdown_cells")
def test_latex_and_pdf(ipynb_app):
    ipynb_app.run(
        {
            "conversion": "latex_ipypublish_main",
            "default_pporder_kwargs": {"create_pdf": True},
        }
    )
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_exists(extension=".pdf")
    # Table format has changed through the versions
    if ipynb_app.pandoc_version < "2.2":
        raise AssertionError("pandoc version must be >= 2.2")
    ipynb_app.assert_converted_equals_expected("latex_ipypublish_main.pandoc.2-2")


@pytest.mark.ipynb("nb_markdown_cells")
def test_sphinx_rst(ipynb_app):
    ipynb_app.run({"conversion": "sphinx_ipypublish_main"})
    ipynb_app.assert_converted_exists()
    # Table format has changed through the versions
    if ipynb_app.pandoc_version < "2.6":
        raise AssertionError("pandoc version must be >= 2.6")
    ipynb_app.assert_converted_equals_expected("sphinx_ipypublish_main.pandoc.2-6")


@pytest.mark.ipynb("nb_with_mkdown_images")  # out_to_temp=False
def test_sphinx_rst_with_mkdown_images(ipynb_app):
    """ test a notebook with multiple images """
    ipynb_app.run(
        {
            "conversion": "sphinx_ipypublish_main.run",
            "log_to_file": True,
            "default_pporder_kwargs": {"dump_files": True},
        }
    )
    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_equals_expected("sphinx_ipypublish_main")
    assert ipynb_app.converted_path.joinpath("main_files/example.jpg").is_file()
