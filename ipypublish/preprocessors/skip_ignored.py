from nbconvert.preprocessors import Preprocessor
from nbformat import NotebookNode


class SkipIgnored(Preprocessor):
    """
    A Preprocessor which omits any cell with the metadata ipub.ignore set to True.
    """

    def preprocess(self, nb, resources):

        def ignored(cell):
            cell.metadata.ipub = cell.metadata.get("ipub", NotebookNode())
            return cell.metadata.ipub.get("ignore", False)

        nb.cells = [cell for cell in nb.cells if not ignored(cell)]
        return nb, resources
