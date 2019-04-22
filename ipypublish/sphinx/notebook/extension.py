import os
from docutils.parsers import rst
from six import string_types

from ipypublish import __version__
from ipypublish.sphinx.utils import import_sphinx

from ipypublish.sphinx.notebook.directives import (
    NbInfo, NbInput, NbOutput, NbWarning,
    AdmonitionNode, CodeAreaNode, FancyOutputNode)
from ipypublish.sphinx.notebook.transforms import (
    CreateDomainObjectLabels, CreateSectionLabels, RewriteLocalLinks
)
from ipypublish.sphinx.notebook.parser import NBParser

try:
    from sphinx.application import Sphinx  # noqa: F401
except ImportError:
    pass


def setup(app):
    # type: (Sphinx) -> dict
    """Initialize Sphinx extension.


    Notes
    -----

    TODO better latex output
    but not really interested in this as it would be duplication of effort,
    and if much better todo ipynb -> tex, rather than ipynb -> rst -> tex
    TODO handling of svg in latex
    ipypublish sets latex to output svg rather than pdf, so we don't have to
    split output into '.. only html/latex', which is an issue its something
    with a label (duplication error), however,
    this requires sphinx.ext.imgconverter to work

    """
    # delayed import of sphinx
    sphinx = import_sphinx()

    try:
        transforms = app.registry.get_transforms()
    except AttributeError:  # Sphinx < 1.7
        from sphinx.io import SphinxStandaloneReader
        transforms = SphinxStandaloneReader.transforms

    def add_transform(transform, post=False):
        if transform not in transforms:
            if post:
                app.add_post_transform(transform)
            else:
                app.add_transform(transform)

    try:
        # Available since Sphinx 1.8:
        app.add_source_parser(NBParser)
    except TypeError:
        # Available since Sphinx 1.4:
        app.add_source_parser('jupyter_notebook', NBParser)

    associate_single_extension(app, '.ipynb', called_from_setup=True)

    # config for export config
    app.add_config_value(
        'ipysphinx_export_config', 'sphinx_ipypublish_all.ext', rebuild='env')

    # config for contolling conversion process
    # where to dump internal images, etc of the notebook
    app.add_config_value(
        'ipysphinx_folder_suffix', "_nbfiles", rebuild='env')
    # whether to raise error if nb_name.rst already exists
    app.add_config_value('ipysphinx_overwrite_existing', False, rebuild='env')
    # additional folders containing conversion files
    app.add_config_value('ipysphinx_config_folders', (), rebuild='env')

    # config for cell prompts
    app.add_config_value('ipysphinx_show_prompts', False, rebuild='env')
    app.add_config_value(
        'ipysphinx_input_prompt', '[{count}]:', rebuild='env')
    app.add_config_value(
        'ipysphinx_output_prompt', '[{count}]:', rebuild='env')

    # config for html css
    app.add_config_value('ipysphinx_responsive_width', '540px', rebuild='html')
    app.add_config_value('ipysphinx_prompt_width', None, rebuild='html')
    # setup html style
    app.connect('builder-inited', set_css_prompts)
    app.connect('html-page-context', html_add_css)

    # config for additions to the output rst (per file)
    # these strings are processed by the exporters jinja template
    app.add_config_value('ipysphinx_prolog', None, rebuild='env')
    app.add_config_value('ipysphinx_epilog', None, rebuild='env')

    # map additional file extensions to pre-converters
    # NB: jupytext is already a default for .Rmd
    app.add_config_value('ipysphinx_preconverters', {}, rebuild='env')
    app.connect('builder-inited', associate_extensions)

    # add the main directives
    app.add_directive('nbinput', NbInput)
    app.add_directive('nboutput', NbOutput)
    app.add_directive('nbinfo', NbInfo)
    app.add_directive('nbwarning', NbWarning)

    # add docutils nodes and visit/depart wraps
    app.add_node(CodeAreaNode,
                 html=(
                     lambda self, node: None,
                     depart_codearea_html
                 ),
                 #  latex=(
                 #      lambda self, node: self.pushbody([]),  # used in depart
                 #      lambda self, node: None,
                 #  )
                 )
    app.add_node(FancyOutputNode,
                 html=(
                     lambda self, node: None,
                     lambda self, node: None,
                 ),
                 #  latex=(
                 #      lambda self, node: None,
                 #      lambda self, node: None,
                 #  )
                 )
    app.add_node(AdmonitionNode,
                 html=(
                     visit_admonition_html,
                     lambda self, node:
                     self.body.append('</div>\n')
                 ),
                 #  latex=(
                 #      lambda self, node:
                 #      self.body.append(
                 #          '\n\\begin{{sphinxadmonition}}{{{class}}}'
                 #          '{{}}\\unskip'.format(node['classes'][1])),
                 #      lambda self, node:
                 #      self.body.append('\\end{sphinxadmonition}\n')
                 #  )
                 )

    # add transformations
    add_transform(CreateSectionLabels)
    add_transform(CreateDomainObjectLabels)
    add_transform(RewriteLocalLinks)

    # Work-around until https://github.com/sphinx-doc/sphinx/pull/5504 is done:
    mathjax_config = app.config._raw_config.setdefault('mathjax_config', {})
    mathjax_config.setdefault(
        'tex2jax',
        {
            'inlineMath': [['$', '$'], ['\\(', '\\)']],
            'processEscapes': True,
            'ignoreClass': 'document',
            'processClass': 'math|output_area',
        }
    )

    # Make docutils' "code" directive (generated by markdown2rst/pandoc)
    # behave like Sphinx's "code-block",
    # see https://github.com/sphinx-doc/sphinx/issues/2155:
    rst.directives.register_directive('code', sphinx.directives.code.CodeBlock)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'env_version': 1,
    }


def associate_extensions(app):
    for suffix in app.config.ipysphinx_preconverters:
        associate_single_extension(app, suffix,
                                   config_value="ipysphinx_preconverters")


def associate_single_extension(app, extension, suffix='jupyter_notebook',
                               called_from_setup=False,
                               config_value=None):
    # type: (Sphinx, str) -> None
    """ associate a file extension with the NBParser

    Notes
    -----
    The Ugly hack to modify source_suffix and source_parsers.
    Once https://github.com/sphinx-doc/sphinx/pull/2209
    is merged it won't be necessary.
    See also https://github.com/sphinx-doc/sphinx/issues/2162.

    """
    if not isinstance(extension, string_types):
        raise AssertionError("extension is not a string: {}".format(extension))
    if not extension.startswith("."):
        raise AssertionError(
            "extension should start with a '.': {}".format(extension))

    sphinx = import_sphinx()

    try:
        # Available since Sphinx 1.8:
        app.add_source_suffix(extension, suffix)
    except AttributeError:

        if not called_from_setup:
            # too late to set up, see
            # https://github.com/sphinx-doc/sphinx/issues/2162#issuecomment-169193107
            raise sphinx.errors.ExtensionError(
                "Using sphinx<1.8, {0} cannot be used.\n"
                "Instead use: source_parsers = "
                "{{'{1}': 'ipypublish.ipysphinx.parser.NBParser'}} "
                "in conf.py".format(config_value, extension))

        source_suffix = app.config._raw_config.get('source_suffix', ['.rst'])

        if isinstance(source_suffix, sphinx.config.string_types):
            source_suffix = [source_suffix]
        if extension not in source_suffix:
            source_suffix.append(extension)
            app.config._raw_config['source_suffix'] = source_suffix
        source_parsers = app.config._raw_config.get('source_parsers', {})

        if (extension not in source_parsers
                and extension[1:] not in source_parsers):
            source_parsers[extension] = NBParser
            app.config._raw_config['source_parsers'] = source_parsers

    sphinx.util.logging.getLogger('nbparser').info(
        "ipypublish: associated {} with NBParser".format(extension))


def visit_admonition_html(self, node):
    """add openeing div and set classes  """
    self.body.append(self.starttag(node, 'div'))
    if len(node.children) >= 2:
        node[0]['classes'].append('admonition-title')
        html_theme = self.settings.env.config.html_theme
        if html_theme in ('sphinx_rtd_theme', 'julia'):
            node.children[0]['classes'].extend(['fa', 'fa-exclamation-circle'])


def depart_codearea_html(self, node):
    """Add empty lines before and after the code."""
    text = self.body[-1]
    text = text.replace('<pre>',
                        '<pre>\n' + '\n' * node.get('empty-lines-before', 0))
    text = text.replace('</pre>',
                        '\n' * node.get('empty-lines-after', 0) + '</pre>')
    self.body[-1] = text


def read_css(name):
    folder = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          "css")
    with open(os.path.join(folder, name + ".css")) as fobj:
        content = fobj.read()

    return content


def set_css_prompts(app):
    """ Set default value for CSS prompt width """
    if app.config.ipysphinx_prompt_width is None:
        app.config.ipysphinx_prompt_width = {
            'agogo': '4ex',
            'alabaster': '5ex',
            'better': '5ex',
            'classic': '4ex',
            'cloud': '5ex',
            'dotted': '5ex',
            'haiku': '4ex',
            'julia': '5ex',
            'nature': '5ex',
            'pyramid': '5ex',
            'redcloud': '5ex',
            'sphinx_py3doc_enhanced_theme': '6ex',
            'sphinx_rtd_theme': '5ex',
            'traditional': '4ex',
        }.get(app.config.html_theme, '7ex')


def html_add_css(app, pagename, templatename, context, doctree):
    """Add CSS string to HTML pages that contain code cells."""
    style = ''
    if doctree and doctree.get('nbsphinx_include_css'):
        style += read_css('nb_cells') % app.config
    if doctree and app.config.html_theme in ('sphinx_rtd_theme', 'julia'):
        style += read_css('sphinx_rtd_theme')
    if doctree and app.config.html_theme in ('cloud', 'redcloud'):
        style += read_css('cloud_theme')
    if style:
        context['body'] = '\n<style>' + style + '</style>\n' + context['body']
