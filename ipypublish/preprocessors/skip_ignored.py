from nbconvert.preprocessors import Preprocessor
from nbformat import NotebookNode


class SkipIgnored(Preprocessor):
    """
    A Preprocessor which omits any cell with the metadata ipub.ignore set to True.
    """

    def preprocess(self, nb, resources):

        def included(cell):
            cell.metadata.ipub = cell.metadata.get("ipub", NotebookNode())
            return not cell.metadata.ipub.get("ignore", False)

        nb.cells = list(filter(included, nb.cells))
        return nb, resources