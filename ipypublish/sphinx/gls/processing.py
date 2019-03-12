"""
Originally adapted from: https://github.com/mcmtroffaes/sphinxcontrib-bibtex
"""
import docutils
import sphinx.util

from ipypublish.sphinx.gls.cache import Cache
from ipypublish.sphinx.gls.bibgloss import latex_to_docutils

logger = sphinx.util.logging.getLogger(__name__)


def init_bibgloss_cache(app):
    """Create ``app.env.bibgloss_cache`` if it does not exist yet.
    :param app: The sphinx application.
    :type app: :class:`sphinx.application.Sphinx`
    """
    if not hasattr(app.env, "bibgloss_cache"):
        app.env.bibgloss_cache = Cache()


def purge_bibgloss_cache(app, env, docname):
    """Remove all information related to *docname* from the cache.
    :param app: The sphinx application.
    :type app: :class:`sphinx.application.Sphinx`
    :param env: The sphinx build environment.
    :type env: :class:`sphinx.environment.BuildEnvironment`
    """
    env.bibgloss_cache.purge(docname)


def process_citations(app, doctree, docname):
    """Replace labels of citation nodes by actual labels.
    :param app: The sphinx application.
    :type app: :class:`sphinx.application.Sphinx`
    :param doctree: The document tree.
    :type doctree: :class:`docutils.nodes.document`
    :param docname: The document name.
    :type docname: :class:`str`
    """
    # citation(rawsource='', *children, **attributes)
    for node in doctree.traverse(docutils.nodes.citation):
        if "bibglossary" not in node.attributes.get('classes', []):
            continue
        key = node[0].astext()
        try:
            label_str = app.env.bibgloss_cache.get_label_from_key(key)
        except KeyError:
            logger.warning("could not relabel glossary item [%s]" % key,
                           type="bibgloss", subtype="relabel")
        else:
            if app.config.bibgloss_convert_latex:
                label = latex_to_docutils(label_str)
                # label(rawsource='', text='', *children, **attributes)
                node[0] = docutils.nodes.label('', '', *label.children[0])
            else:
                node[0] = docutils.nodes.label('', label_str)


def process_citation_references(app, doctree, docname):
    """Replace text of citation reference nodes by actual labels.
    :param app: The sphinx application.
    :type app: :class:`sphinx.application.Sphinx`
    :param doctree: The document tree.
    :type doctree: :class:`docutils.nodes.document`
    :param docname: The document name.
    :type docname: :class:`str`
    """
    # sphinx has already turned citation_reference nodes
    # into reference nodes, so iterate over reference nodes
    # reference(rawsource='', text='', *children, **attributes)
    for node in doctree.traverse(docutils.nodes.reference):
        if "bibglossary" not in node.attributes.get('classes', []):
            continue
        text = node[0].astext()
        key = text[1:-1]
        try:
            if "bibgplural" in node.attributes.get('classes', []):
                label = app.env.bibgloss_cache.get_plural_from_key(key)
            else:
                label = app.env.bibgloss_cache.get_label_from_key(key)
        except KeyError:
            pass
            logger.warning(
                "could not relabel glossary reference [%s]" % key,
                type="bibgloss", subtype="relabel")
        else:
            if "bibgcapital" in node.attributes.get('classes', []):
                label = label.capitalize()

            if app.config.bibgloss_convert_latex:
                # note we use only the first child of the document
                # TODO is this the best way to do this
                label = latex_to_docutils(label)
                node[0] = label.children[0]
            else:
                node[0] = docutils.nodes.Text(label)
