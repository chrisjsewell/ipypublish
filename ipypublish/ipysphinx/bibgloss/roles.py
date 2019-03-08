from sphinx.roles import XRefRole

from ipypublish.bib2glossary.common import get_fake_entry_obj
from ipypublish.bib2glossary.sphinx import docutils_citation_reference_node


class GLSRole(XRefRole):
    """Class for processing the `gls` role."""

    def result_nodes(self, document, env, node, is_ref):
        """Transform reference node into a citation reference,
        and note that the reference was cited.
        """
        keys = node['reftarget'].split(',')
        # Note that at this point, usually, env.bibgloss_cache.bibfiles
        # is still empty because the bibliography directive may not
        # have been processed yet, so we cannot get the actual entry.
        # Instead, we simply fake an entry with the desired key, and
        # fix the label at doctree-resolved time. This happens in
        # process_citation_references.
        refnodes = [
            docutils_citation_reference_node(get_fake_entry_obj(key), document)
            for key in keys]
        for key in keys:
            env.bibgloss_cache.add_cited(key, env.docname)
        return refnodes, []
