from docutils import nodes


class AdmonitionNode(nodes.Element):
    """A custom node for info and warning boxes."""


class CodeAreaNode(nodes.Element):
    """Input area or output area of a Jupyter notebook code cell."""


class FancyOutputNode(nodes.Element):
    """A custom node for non-code output of code cells."""
