"""
adapted from nbsphinx
"""
import docutils
from docutils import nodes  # noqa E501
from docutils.parsers import rst
from docutils.statemachine import StringList

from ipypublish.sphinx.utils import import_sphinx
from ipypublish.sphinx.notebook.nodes import (
    AdmonitionNode, CodeAreaNode, FancyOutputNode
)


class NbAdmonition(rst.Directive):
    """Base class for NbInfo and NbWarning."""

    required_arguments = 0
    optional_arguments = 0
    option_spec = {}
    has_content = True

    def run(self):
        """This is called by the reST parser."""
        node = AdmonitionNode(classes=['admonition', self._class])
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class NbWarning(NbAdmonition):
    """A warning box."""

    _class = 'warning'


class NbInfo(NbAdmonition):
    """An information box."""

    _class = 'note'


class NbInput(rst.Directive):
    """A notebook input cell with prompt and code area."""

    required_arguments = 0
    optional_arguments = 1  # lexer name
    final_argument_whitespace = False
    option_spec = {
        'execution-count': rst.directives.positive_int,
        'empty-lines-before': rst.directives.nonnegative_int,
        'empty-lines-after': rst.directives.nonnegative_int,
        'no-output': rst.directives.flag,
        'caption': rst.directives.unchanged,
        'name': rst.directives.unchanged
    }
    has_content = True

    def run(self):
        """This is called by the reST parser."""
        self.state.document['nbsphinx_include_css'] = True
        return _create_nbcell_nodes(self)


class NbOutput(rst.Directive):
    """A notebook output cell with optional prompt."""

    required_arguments = 0
    optional_arguments = 1  # 'rst' or nothing (which means literal text)
    final_argument_whitespace = False
    option_spec = {
        'execution-count': rst.directives.positive_int,
        'more-to-come': rst.directives.flag,
        'empty-lines-before': rst.directives.nonnegative_int,
        'empty-lines-after': rst.directives.nonnegative_int,
        'class': rst.directives.unchanged,
    }
    has_content = True

    def run(self):
        """This is called by the reST parser."""
        self.state.document['nbsphinx_include_css'] = True
        return _create_nbcell_nodes(self)


def _create_nbcell_nodes(directive):
    """Create nodes for an input or output notebook cell."""

    sphinx = import_sphinx()

    language = 'none'
    prompt = ''
    fancy_output = False
    execution_count = directive.options.get('execution-count')
    config = directive.state.document.settings.env.config

    if isinstance(directive, NbInput):
        outer_classes = ['nbinput']
        if 'no-output' in directive.options:
            outer_classes.append('nblast')
        inner_classes = ['input_area']
        if directive.arguments:
            language = directive.arguments[0]
        prompt_template = config.ipysphinx_input_prompt
        if not execution_count:
            execution_count = ' '
    elif isinstance(directive, NbOutput):
        outer_classes = ['nboutput']
        if 'more-to-come' not in directive.options:
            outer_classes.append('nblast')
        inner_classes = ['output_area']
        # 'class' can be 'stderr'
        inner_classes.append(directive.options.get('class', ''))
        prompt_template = config.ipysphinx_output_prompt
        if directive.arguments and directive.arguments[0] in ['rst', 'ansi']:
            fancy_output = True
    else:
        raise AssertionError("directive should be NbInput or NbOutput")

    outer_node = docutils.nodes.container(classes=outer_classes)

    # add prompts
    if config.ipysphinx_show_prompts and execution_count:
        prompt = prompt_template.format(count=execution_count)
        prompt_node = docutils.nodes.literal_block(
            prompt, prompt, language='none', classes=['prompt'])
    elif config.ipysphinx_show_prompts:
        prompt = ''
        prompt_node = docutils.nodes.container(classes=['prompt', 'empty'])
    if config.ipysphinx_show_prompts:
        # NB: Prompts are added manually in LaTeX output
        outer_node += sphinx.addnodes.only('', prompt_node, expr='html')

    if fancy_output:
        inner_node = docutils.nodes.container(classes=inner_classes)
        sphinx.util.nodes.nested_parse_with_titles(
            directive.state, directive.content, inner_node)
        outtype = directive.arguments[0]
        if outtype == 'rst':
            outer_node += FancyOutputNode('', inner_node, prompt=prompt)
        elif outtype == 'ansi':
            outer_node += inner_node
        else:
            raise AssertionError(
                "`.. nboutput:: type` should be 'rst' or 'ansi', "
                "not: {}".format(outtype))
    else:
        text = '\n'.join(directive.content.data)
        inner_node = docutils.nodes.literal_block(
            text, text, language=language, classes=inner_classes)
        codearea_node = CodeAreaNode('', inner_node, prompt=prompt)
        # create a literal text block (e.g. with the code-block directive),
        # that starts or ends with a blank line
        # (see http://stackoverflow.com/q/34050044/)
        for attr in 'empty-lines-before', 'empty-lines-after':
            value = directive.options.get(attr, 0)
            if value:
                codearea_node[attr] = value

        # add caption and label, see:
        if directive.options.get("caption", False):
            caption = directive.options.get("caption")
            wrapper = container_wrapper(
                directive, inner_node, caption, inner_classes)
            # add label
            directive.add_name(wrapper)
            outer_node += wrapper
        else:
            outer_node += codearea_node

    return [outer_node]


def container_wrapper(directive, literal_node, caption, classes):
    """adapted from
    https://github.com/sphinx-doc/sphinx/blob/master/sphinx/directives/code.py
    """
    container_node = docutils.nodes.container(
        '', literal_block=True, classes=classes)  # ['literal-block-wrapper']
    parsed = docutils.nodes.Element()
    directive.state.nested_parse(StringList([caption], source=''),
                                 directive.content_offset, parsed)
    if isinstance(parsed[0], docutils.nodes.system_message):
        msg = 'Invalid caption: %s' % parsed[0].astext()
        raise ValueError(msg)
    elif isinstance(parsed[0], docutils.nodes.Element):
        caption_node = docutils.nodes.caption(parsed[0].rawsource, '',
                                              *parsed[0].children)
        caption_node.source = literal_node.source
        caption_node.line = literal_node.line
        container_node += caption_node
        container_node += literal_node
        return container_node
    else:
        raise RuntimeError  # never reached
