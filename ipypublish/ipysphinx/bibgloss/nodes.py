from docutils import nodes


class BibGlossaryNode(nodes.General, nodes.Element):

    """Node for representing a bibglossary. Replaced by a list of
    glossary terms by
    :class:`~ipypublish.ipysphinx.bibgloss.transforms.BibGlossaryTransform`.
    """
    pass