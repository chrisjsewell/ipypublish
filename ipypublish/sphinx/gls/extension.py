from ipypublish import __version__
from ipypublish.sphinx.utils import import_sphinx

from ipypublish.sphinx.gls import processing as bibproc
from ipypublish.sphinx.gls.directives import BibGlossaryDirective
from ipypublish.sphinx.gls.roles import (
    GLSRole, GLSCapitalRole, GLSPluralRole, GLSPluralCapitalRole)
from ipypublish.sphinx.gls.nodes import BibGlossaryNode
from ipypublish.sphinx.gls.transforms import (
    BibGlossaryTransform, OverrideCitationReferences,
    HandleMissingCitesTransform)

try:
    from sphinx.application import Sphinx  # noqa: F401
except ImportError:
    pass


def setup(app):
    # type: (Sphinx) -> dict
    """Initialize Sphinx extension.

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

    # BibGlossary functionality
    app.connect("builder-inited", bibproc.init_bibgloss_cache)
    app.connect("doctree-resolved", bibproc.process_citations)
    app.connect("doctree-resolved", bibproc.process_citation_references)
    app.connect("env-purge-doc", bibproc.purge_bibgloss_cache)
    # app.connect("env-updated", bibproc.check_duplicate_labels)
    app.add_config_value('bibgloss_convert_latex', True, rebuild='html')
    app.add_config_value('bibgloss_default_style', 'list', rebuild='html')

    app.add_directive("bibglossary", BibGlossaryDirective)
    # Note: because docutils.parsers.rst.roles.role(role_name)
    #       applies role_name.lower(), you can't have unique gls and Gls roles
    app.add_role("gls", GLSRole())
    app.add_role("glsc", GLSCapitalRole())
    app.add_role("glspl", GLSPluralRole())
    app.add_role("glscpl", GLSPluralCapitalRole())
    app.add_node(BibGlossaryNode, override=True)

    add_transform(BibGlossaryTransform)
    # these patches have been fixed (by me!) upstream
    if sphinx.version_info < (2,):
        add_transform(OverrideCitationReferences)
        add_transform(HandleMissingCitesTransform, post=True)

    # Parallel read is not safe at the moment: in the current design,
    # the document that contains references must be read last for all
    # references to be resolved.
    parallel_read_safe = False

    return {
        'version': __version__,
        'parallel_read_safe': parallel_read_safe,
        'parallel_write_safe': True,
        'env_version': 1,
    }
