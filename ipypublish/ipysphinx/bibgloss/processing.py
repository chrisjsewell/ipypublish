import docutils
import six
import sphinx.util

from ipypublish.ipysphinx.bibgloss.cache import Cache

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
    for node in doctree.traverse(docutils.nodes.citation):
        if "bibglossary" not in node.attributes.get('classes', []):
            continue
        key = node[0].astext()
        try:
            label = app.env.bibgloss_cache.get_label_from_key(key)
        except KeyError:
            logger.warning("could not relabel glossary item [%s]" % key)
        else:
            node[0] = docutils.nodes.label('', label)


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
                "could not relabel glossary reference [%s]" % key)
        else:
            if "bibgcapital" in node.attributes.get('classes', []):
                label = label.capitalize()
            node[0] = docutils.nodes.Text(label)


def check_duplicate_labels(app, env):
    """Check and warn about duplicate glossary labels.
    :param app: The sphinx application.
    :type app: :class:`sphinx.application.Sphinx`
    :param env: The sphinx build environment.
    :type env: :class:`sphinx.environment.BuildEnvironment`
    """
    label_to_key = {}
    for info in env.bibgloss_cache.get_all_bibliography_caches():
        for key, label in six.iteritems(info.labels):
            if label in label_to_key:
                logger.warning(
                    "duplicate glossary label for keys %s and %s"
                    % (key, label_to_key[label]))
            else:
                label_to_key[label] = key
