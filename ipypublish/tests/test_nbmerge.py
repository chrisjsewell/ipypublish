import pytest
from ipypublish.convert import nbmerge


@pytest.mark.ipynb('basic_nb')
def test_nbmerge_one_notebook(ipynb_app):
    nb, path = nbmerge.merge_notebooks(ipynb_app.source_path)
    assert nb.metadata.test_name == "notebook1"
    assert len(nb.cells) == 2


@pytest.mark.ipynb('merge_nbs', main_file=None)
def test_nbmerge_two_notebooks(ipynb_app):
    nb, path = nbmerge.merge_notebooks(ipynb_app.source_path)
    assert nb.metadata.test_name == "notebook1"
    assert len(nb.cells) == 4


@pytest.mark.ipynb('merge_nbs', main_file=None)
def test_merge_latex(ipynb_app):
    ipynb_app.run()
    ipynb_app.assert_converted_exists()
