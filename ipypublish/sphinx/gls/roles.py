from sphinx.roles import XRefRole

from ipypublish.bib2glossary import BibGlossDB
from ipypublish.sphinx.gls.bibgloss import docutils_citation_ref_node


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
            docutils_citation_ref_node(
                BibGlossDB.get_fake_entry_obj(key),
                document, classes=["bibglossary"])
            for key in keys]
        for key in keys:
            env.bibgloss_cache.add_cited(key, env.docname)
        return refnodes, []


class GLSCapitalRole(XRefRole):
    """Class for processing the `glsc` role."""

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
            docutils_citation_ref_node(
                BibGlossDB.get_fake_entry_obj(key), document,
                classes=["bibglossary", "bibgcapital"])
            for key in keys]
        for key in keys:
            env.bibgloss_cache.add_cited(key, env.docname)
        return refnodes, []


class GLSPluralRole(XRefRole):
    """Class for processing the `glspl` role."""

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
            docutils_citation_ref_node(
                BibGlossDB.get_fake_entry_obj(key), document,
                classes=["bibglossary", "bibgplural"])
            for key in keys]
        for key in keys:
            env.bibgloss_cache.add_cited(key, env.docname)
        return refnodes, []


class GLSPluralCapitalRole(XRefRole):
    """Class for processing the `glscpl` role."""

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
            docutils_citation_ref_node(
                BibGlossDB.get_fake_entry_obj(key), document,
                classes=["bibglossary", "bibgplural", "bibgcapital"])
            for key in keys]
        for key in keys:
            env.bibgloss_cache.add_cited(key, env.docname)
        return refnodes, []
