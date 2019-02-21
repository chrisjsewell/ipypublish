
import ruamel.yaml as yaml
from nbformat.notebooknode import NotebookNode


def recurse_convert(node):
    # type: (NotebookNode) -> dict
    """convert notebook node to dict"""
    dct = {}
    for key, val in node.items():
        if isinstance(val, NotebookNode):
            dct[key] = recurse_convert(val)
        else:
            dct[key] = val
    return dct


def meta_to_yaml(metadata, comment="#~~ "):
    # type: (NotebookNode, str) -> str
    """convert metadata json to yaml

    Parameters
    ----------
    metadata: nbformat.notebooknode.NotebookNode
    comment="": str
        append to the start of each line

    Returns
    -------
    string: str

    """
    metadata = recurse_convert(metadata)
    string = yaml.dump(metadata, default_flow_style=False)
    if comment:
        string = "\n".join([comment + s for s in string.splitlines()])
    return string
