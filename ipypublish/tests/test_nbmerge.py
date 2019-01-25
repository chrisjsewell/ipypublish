from ipypublish.scripts import nbmerge


def test_nbmerge_one_notebook(ipynb1):
    nb, path = nbmerge.merge_notebooks(ipynb1)
    assert nb.metadata.test_name == "notebook1"
    assert len(nb.cells) == 2


def test_nbmerge_two_notebooks(directory):
    nb, path = nbmerge.merge_notebooks(directory)
    assert nb.metadata.test_name == "notebook2"
    assert len(nb.cells) == 4
