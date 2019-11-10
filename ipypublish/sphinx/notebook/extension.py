import io
import os
from docutils.parsers import rst
import six

from ipypublish import __version__
from ipypublish.sphinx.utils import import_sphinx

from ipypublish.sphinx.notebook.directives import (
    NbInfo,
    NbInput,
    NbOutput,
    NbWarning,
    AdmonitionNode,
    NBInputToggle,
    NBOutputToggle,
    CodeAreaNode,
    FancyOutputNode,
)
from ipypublish.sphinx.notebook.transforms import (
    CreateDomainObjectLabels,
    CreateSectionLabels,
    RewriteLocalLinks,
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

    transforms = app.registry.get_transforms()

    def add_transform(transform, post=False):
        if transform not in transforms:
            if post:
                app.add_post_transform(transform)
            else:
                app.add_transform(transform)

    app.add_source_parser(NBParser)

    associate_single_extension(app, ".ipynb")

    # config for export config
    app.add_config_value(
        "ipysphinx_export_config", "sphinx_ipypublish_all.ext", rebuild="env"
    )

    # config for contolling conversion process
    # where to dump internal images, etc of the notebook
    app.add_config_value("ipysphinx_folder_suffix", "_nbfiles", rebuild="env")
    # whether to raise error if nb_name.rst already exists
    app.add_config_value("ipysphinx_overwrite_existing", False, rebuild="env")
    # additional folders containing conversion files
    app.add_config_value("ipysphinx_config_folders", (), rebuild="env")

    # config for cell prompts
    app.add_config_value("ipysphinx_show_prompts", False, rebuild="env")
    app.add_config_value("ipysphinx_input_prompt", "[{count}]:", rebuild="env")
    app.add_config_value("ipysphinx_output_prompt", "[{count}]:", rebuild="env")

    # config for cell toggling
    app.add_config_value("ipysphinx_input_toggle", False, rebuild="env")
    app.add_config_value("ipysphinx_output_toggle", False, rebuild="env")

    # config for html css
    app.add_config_value("ipysphinx_responsive_width", "540px", rebuild="html")
    app.add_config_value("ipysphinx_prompt_width", None, rebuild="html")
    # setup html style
    app.connect("config-inited", set_css_prompts)
    app.connect("html-page-context", html_add_css)
    # add javascript
    app.connect("html-page-context", html_add_javascript)
    # config for displaying ipywidgets
    app.add_config_value("ipysphinx_always_add_jsurls", False, rebuild="html")
    app.add_config_value("ipysphinx_require_jsurl", None, rebuild="html")
    app.add_config_value("ipysphinx_requirejs_options", None, rebuild="html")
    app.connect("env-updated", add_require_js_path)
    app.add_config_value("ipysphinx_widgets_jsurl", None, rebuild="html")
    app.add_config_value("ipysphinx_widgetsjs_options", {}, rebuild="html")
    app.connect("env-updated", add_ipywidgets_js_path)
    app.connect("env-purge-doc", discard_document_variables)

    # config for additions to the output rst (per file)
    # these strings are processed by the exporters jinja template
    app.add_config_value("ipysphinx_prolog", None, rebuild="env")
    app.add_config_value("ipysphinx_epilog", None, rebuild="env")

    # map additional file extensions to pre-converters
    # NB: jupytext is already a default for .Rmd
    app.add_config_value("ipysphinx_preconverters", {}, rebuild="env")
    app.connect("config-inited", associate_extensions)

    # add the main directives
    app.add_directive("nbinput", NbInput)
    app.add_directive("nboutput", NbOutput)
    app.add_directive("nbinfo", NbInfo)
    app.add_directive("nbwarning", NbWarning)
    app.add_directive("nbinput-toggle-all", NBInputToggle)
    app.add_directive("nboutput-toggle-all", NBOutputToggle)

    # add docutils nodes and visit/depart wraps
    app.add_node(
        CodeAreaNode,
        html=(lambda self, node: None, depart_codearea_html),
        #  latex=(
        #      lambda self, node: self.pushbody([]),  # used in depart
        #      lambda self, node: None,
        #  )
    )
    app.add_node(
        FancyOutputNode,
        html=(lambda self, node: None, lambda self, node: None),
        #  latex=(
        #      lambda self, node: None,
        #      lambda self, node: None,
        #  )
    )
    app.add_node(
        AdmonitionNode,
        html=(visit_admonition_html, lambda self, node: self.body.append("</div>\n")),
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
    mathjax_config = app.config._raw_config.setdefault("mathjax_config", {})
    mathjax_config.setdefault(
        "tex2jax",
        {
            "inlineMath": [["$", "$"], ["\\(", "\\)"]],
            "processEscapes": True,
            "ignoreClass": "document",
            "processClass": "math|output_area",
        },
    )

    # Make docutils' "code" directive (generated by markdown2rst/pandoc)
    # behave like Sphinx's "code-block",
    # see https://github.com/sphinx-doc/sphinx/issues/2155:
    rst.directives.register_directive("code", sphinx.directives.code.CodeBlock)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
        "env_version": 1,
    }


def associate_extensions(app, config):
    for suffix in config.ipysphinx_preconverters:
        associate_single_extension(app, suffix, config_value="ipysphinx_preconverters")


def associate_single_extension(app, extension, suffix="jupyter_notebook"):
    # type: (Sphinx, str) -> None
    """Associate a file extension with the NBParser."""
    if not isinstance(extension, six.string_types):
        raise AssertionError("extension is not a string: {}".format(extension))
    if not extension.startswith("."):
        raise AssertionError("extension should start with a '.': {}".format(extension))

    sphinx = import_sphinx()

    app.add_source_suffix(extension, suffix)
    sphinx.util.logging.getLogger("nbparser").info(
        "ipypublish: associated {} with NBParser".format(extension), color="green"
    )


def visit_admonition_html(self, node):
    """add openeing div and set classes  """
    self.body.append(self.starttag(node, "div"))
    if len(node.children) >= 2:
        node[0]["classes"].append("admonition-title")
        html_theme = self.settings.env.config.html_theme
        if html_theme in ("sphinx_rtd_theme", "julia"):
            node.children[0]["classes"].extend(["fa", "fa-exclamation-circle"])


def depart_codearea_html(self, node):
    """Add empty lines before and after the code."""
    text = self.body[-1]
    text = text.replace("<pre>", "<pre>\n" + "\n" * node.get("empty-lines-before", 0))
    text = text.replace("</pre>", "\n" * node.get("empty-lines-after", 0) + "</pre>")
    self.body[-1] = text


def read_css(name):
    """Return the contents of a CSS file resource."""
    # TODO use importlib_resources to access CSS file content
    folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "css")
    with io.open(os.path.join(folder, name + ".css")) as fobj:
        content = fobj.read()

    return content


def set_css_prompts(app, config):
    """Set default value for CSS prompt width (optimized for two-digit numbers)."""
    if config.ipysphinx_prompt_width is None:
        config.ipysphinx_prompt_width = {
            "agogo": "4ex",
            "alabaster": "5ex",
            "better": "5ex",
            "classic": "4ex",
            "cloud": "5ex",
            "dotted": "5ex",
            "guzzle_sphinx_theme": "6ex",
            "haiku": "4ex",
            "julia": "5ex",
            "maisie_sphinx_theme": "6ex",
            "nature": "5ex",
            "pangeo": "5ex",
            "pyramid": "5ex",
            "redcloud": "5ex",
            "sizzle": "5.5ex",
            "sphinx_py3doc_enhanced_theme": "6ex",
            "sphinx_pyviz_theme": "5.5ex",
            "sphinx_rtd_theme": "5ex",
            "sphinx_typlog_theme": "5.5ex",
            "traditional": "4ex",
        }.get(config.html_theme, "7ex")


def html_add_css(app, pagename, templatename, context, doctree):
    """Add CSS string to HTML pages that contain code cells."""
    style = ""
    if doctree and doctree.get("ipysphinx_include_css"):
        style += read_css("nb_cells") % app.config
    if doctree and app.config.html_theme in ("sphinx_rtd_theme", "julia"):
        style += read_css("sphinx_rtd_theme")
    if doctree and app.config.html_theme in ("cloud", "redcloud"):
        style += read_css("cloud_theme")
    if style:
        context["body"] = "\n<style>" + style + "</style>\n" + context["body"]


def copy_javascript(name):
    """Return the contents of javascript resource file."""
    # TODO use importlib_resources to access javascript file content
    folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "js")
    with open(os.path.join(folder, name + ".js")) as fobj:
        content = fobj.read()

    return content


def html_add_javascript(app, pagename, templatename, context, doctree):
    """Add JavaScript string to HTML pages that contain code cells."""
    if doctree and doctree.get("ipysphinx_include_js"):
        code = copy_javascript("toggle_code")
        context["body"] = "\n<script>" + code + "</script>\n" + context["body"]
        code = copy_javascript("toggle_output")
        context["body"] = "\n<script>" + code + "</script>\n" + context["body"]


def add_require_js_path(app, env):
    """Insert the require javascript package url, to pages created from notebooks."""
    config = app.config
    if not (
        getattr(env, "ipysphinx_created_from_nb", set())
        or config.ipysphinx_always_add_jsurls
    ):
        return
    if config.ipysphinx_require_jsurl is None:
        requirejs_path = (
            "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js"
        )
    else:
        requirejs_path = config.ipysphinx_require_jsurl
    if config.ipysphinx_requirejs_options is None:
        requirejs_options = {
            "integrity": "sha256-Ae2Vz/4ePdIu6ZyI/5ZGsYnb+m0JlOmKPjt6XZ9JJkA=",
            "crossorigin": "anonymous",
        }
    else:
        requirejs_options = config.ipysphinx_requirejs_options

    app.add_js_file(requirejs_path, **requirejs_options)


def add_ipywidgets_js_path(app, env):
    """Insert the ipywidgets javascript url, to pages created from notebooks containing widgets."""
    if not (
        getattr(env, "ipysphinx_widgets", set())
        or app.config.ipysphinx_always_add_jsurls
    ):
        return
    sphinx = import_sphinx()
    widgets_path = None
    if app.config.ipysphinx_widgets_jsurl is None:
        try:
            from ipywidgets.embed import DEFAULT_EMBED_REQUIREJS_URL
        except ImportError:
            logger = sphinx.util.logging.getLogger(__name__)
            logger.warning(
                "ipysphinx_widgets_jsurl not given and ipywidgets module unavailable"
            )
        else:
            widgets_path = DEFAULT_EMBED_REQUIREJS_URL
    else:
        widgets_path = app.config.ipysphinx_widgets_jsurl
    if widgets_path is not None:
        app.add_js_file(widgets_path, **app.config.ipysphinx_widgetsjs_options)


def discard_document_variables(app, env, docname):
    """Discard any document specific variables."""
    # Discard any ipywidgets gathered from the current notebook.
    try:
        env.ipysphinx_widgets.discard(docname)
    except AttributeError:
        pass
    try:
        env.ipysphinx_created_from_nb.discard(docname)
    except AttributeError:
        pass
