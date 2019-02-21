"""
adapted from nbsphinx
"""
import re
import os
try:
    from urllib.parse import unquote  # Python 3.x
except ImportError:
    from urllib2 import unquote  # Python 2.x

import docutils
import nbconvert

from ipypublish.ipysphinx.directives import AdmonitionNode
from ipypublish.ipysphinx.utils import import_sphinx


class ReplaceAlertDivs(docutils.transforms.Transform):
    """Replace certain <div> elements with AdmonitionNode containers.

    This is a quick-and-dirty work-around until a proper
    Mardown/CommonMark extension for note/warning boxes is available.

    """

    default_priority = 500  # Doesn't really matter

    _start_re = re.compile(
        r'\s*<div\s*class\s*=\s*(?P<q>"|\')([a-z\s-]*)(?P=q)\s*>\s*\Z',
        flags=re.IGNORECASE)
    _class_re = re.compile(r'\s*alert\s*alert-(info|warning)\s*\Z')
    _end_re = re.compile(r'\s*</div\s*>\s*\Z', flags=re.IGNORECASE)

    def apply(self):
        start_tags = []
        for node in self.document.traverse(docutils.nodes.raw):
            if node['format'] != 'html':
                continue
            start_match = self._start_re.match(node.astext())
            if not start_match:
                continue
            class_match = self._class_re.match(start_match.group(2))
            if not class_match:
                continue
            admonition_class = class_match.group(1)
            if admonition_class == 'info':
                admonition_class = 'note'
            start_tags.append((node, admonition_class))

        # Reversed order to allow nested <div> elements:
        for node, admonition_class in reversed(start_tags):
            content = []
            for sibling in node.traverse(include_self=False, descend=False,
                                         siblings=True, ascend=False):
                end_tag = (isinstance(sibling, docutils.nodes.raw) and
                           sibling['format'] == 'html' and
                           self._end_re.match(sibling.astext()))
                if end_tag:
                    admonition_node = AdmonitionNode(
                        classes=['admonition', admonition_class])
                    admonition_node.extend(content)
                    parent = node.parent
                    parent.replace(node, admonition_node)
                    for n in content:
                        parent.remove(n)
                    parent.remove(sibling)
                    break
                else:
                    content.append(sibling)


class CopyLinkedFiles(docutils.transforms.Transform):
    """Mark linked (local) files to be copied to the HTML output."""
    default_priority = 600  # After RewriteLocalLinks

    def apply(self):
        sphinx = import_sphinx()
        env = self.document.settings.env
        for node in self.document.traverse(docutils.nodes.reference):
            base, suffix, fragment = _local_file_from_reference(node,
                                                                self.document)
            if not base:
                continue  # Not a local link
            relpath = base + suffix + fragment
            file = os.path.normpath(
                os.path.join(os.path.dirname(env.docname), relpath))
            if not os.path.isfile(os.path.join(env.srcdir, file)):
                logger = sphinx.util.logging.getLogger(__name__)
                logger.warning('File not found: %r', file, location=node)
                continue  # Link is ignored
            elif file.startswith('..'):
                logger = sphinx.util.logging.getLogger(__name__)
                logger.warning('Link outside source directory: %r', file,
                               location=node)
                continue  # Link is ignored
            if not hasattr(env, 'nbsphinx_files'):
                env.nbsphinx_files = {}
            env.nbsphinx_files.setdefault(env.docname, []).append(file)


class CreateNotebookSectionAnchors(docutils.transforms.Transform):
    """Create section anchors for Jupyter notebooks.

    Note: Sphinx lower-cases the HTML section IDs, Jupyter doesn't.
    This transform creates anchors in the Jupyter style.

    # TODO do this in pandoc filter?
    """

    default_priority = 200  # Before CreateSectionLabels (250)

    def apply(self):
        for section in self.document.traverse(docutils.nodes.section):
            title = section.children[0].astext()
            link_id = title.replace(' ', '-')
            section['ids'] = [link_id]


def _local_file_from_reference(node, document):
    """Get local file path from reference and split it into components."""
    # NB: Anonymous hyperlinks must be already resolved at this point!
    refuri = node.get('refuri')
    if not refuri:
        refname = node.get('refname')
        if refname:
            refid = document.nameids.get(refname)
        else:
            # NB: This can happen for anonymous hyperlinks
            refid = node.get('refid')
        target = document.ids.get(refid)
        if not target:
            # No corresponding target, Sphinx may warn later
            return '', '', ''
        refuri = target.get('refuri')
        if not refuri:
            # Target doesn't have URI
            return '', '', ''
    if '://' in refuri:
        # Not a local link
        return '', '', ''
    elif refuri.startswith('#') or refuri.startswith('mailto:'):
        # Not a local link
        return '', '', ''

    # NB: We look for "fragment identifier" before unquoting
    match = re.match(r'^([^#]+)(\.[^#]+)(#.+)$', refuri)
    if match:
        base = unquote(match.group(1))
        # NB: The suffix and "fragment identifier" are not unquoted
        suffix = match.group(2)
        fragment = match.group(3)
    else:
        base, suffix = os.path.splitext(refuri)
        base = unquote(base)
        fragment = ''
    return base, suffix, fragment


class RewriteLocalLinks(docutils.transforms.Transform):
    """Turn links to source files into ``:doc:``/``:ref:`` links.

    Links to subsections are possible with ``...#Subsection-Title``.
    These links use the labels created by CreateSectionLabels.

    Links to subsections use ``:ref:``, links to whole source files use
    ``:doc:``.  Latter can be useful if you have an ``index.rst`` but
    also want a distinct ``index.ipynb`` for use with Jupyter.
    In this case you can use such a link in a notebook::

        [Back to main page](index.ipynb)

    In Jupyter, this will create a "normal" link to ``index.ipynb``, but
    in the files generated by Sphinx, this will become a link to the
    main page created from ``index.rst``.

    """

    default_priority = 500  # After AnonymousHyperlinks (440)

    def apply(self):
        sphinx = import_sphinx()
        env = self.document.settings.env
        for node in self.document.traverse(docutils.nodes.reference):
            base, suffix, fragment = _local_file_from_reference(node,
                                                                self.document)
            if not base:
                continue

            for s in env.config.source_suffix:
                if suffix.lower() == s.lower():
                    target = base
                    if fragment:
                        target_ext = suffix + fragment
                        reftype = 'ref'
                    else:
                        target_ext = ''
                        reftype = 'doc'
                    break
            else:
                continue  # Not a link to a potential Sphinx source file

            target_docname = nbconvert.filters.posix_path(os.path.normpath(
                os.path.join(os.path.dirname(env.docname), target)))
            if target_docname in env.found_docs:
                reftarget = '/' + target_docname + target_ext
                if reftype == 'ref':
                    reftarget = reftarget.lower()
                linktext = node.astext()
                xref = sphinx.addnodes.pending_xref(
                    reftype=reftype, reftarget=reftarget, refdomain='std',
                    refwarn=True, refexplicit=True, refdoc=env.docname)
                xref += docutils.nodes.Text(linktext, linktext)
                node.replace_self(xref)


class CreateSectionLabels(docutils.transforms.Transform):
    """Make labels for each document and each section thereof.

    These labels are referenced in RewriteLocalLinks but can also be
    used manually with ``:ref:``.

    """

    default_priority = 250  # Before references.PropagateTargets (260)

    def apply(self):
        env = self.document.settings.env
        file_ext = os.path.splitext(env.doc2path(env.docname))[1]
        i_still_have_to_create_the_document_label = True
        for section in self.document.traverse(docutils.nodes.section):
            assert section.children
            assert isinstance(section.children[0], docutils.nodes.title)
            title = section.children[0].astext()
            link_id = section['ids'][0]
            label = '/' + env.docname + file_ext + '#' + link_id
            label = label.lower()
            env.domaindata['std']['labels'][label] = (
                env.docname, link_id, title)
            env.domaindata['std']['anonlabels'][label] = (
                env.docname, link_id)

            # Create a label for the whole document using the first section:
            if i_still_have_to_create_the_document_label:
                label = '/' + env.docname.lower() + file_ext
                env.domaindata['std']['labels'][label] = (
                    env.docname, '', title)
                env.domaindata['std']['anonlabels'][label] = (
                    env.docname, '')
                i_still_have_to_create_the_document_label = False


class CreateDomainObjectLabels(docutils.transforms.Transform):
    """Create labels for domain-specific object signatures."""

    default_priority = 250  # About the same as CreateSectionLabels

    def apply(self):
        sphinx = import_sphinx()
        env = self.document.settings.env
        file_ext = os.path.splitext(env.doc2path(env.docname))[1]
        for sig in self.document.traverse(sphinx.addnodes.desc_signature):
            try:
                title = sig['ids'][0]
            except IndexError:
                # Object has same name as another, so skip it
                continue
            link_id = title.replace(' ', '-')
            sig['ids'] = [link_id]
            label = '/' + env.docname + file_ext + '#' + link_id
            label = label.lower()
            env.domaindata['std']['labels'][label] = (
                env.docname, link_id, title)
            env.domaindata['std']['anonlabels'][label] = (
                env.docname, link_id)
