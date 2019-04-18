import docutils

from ipypublish.bib2glossary import BibGlossEntry


def docutils_citation_ref_node(
        entry, document, use_key_as_label=True, classes=('bibglossary',)):
    # type: (dict, docutils.nodes.document, bool) -> docutils.nodes.citation_reference  # noqa
    """Return citation_reference node to the given citation. The
    citation_reference is expected to be inserted into *document*
    prior to any docutils transforms.
    """
    if not isinstance(entry, BibGlossEntry):
        raise TypeError
    # see docutils.parsers.rst.states.Body.footnote_reference()
    if use_key_as_label:
        label = entry.key
    else:
        label = entry.label
    refname = docutils.nodes.fully_normalize_name(entry.key)
    refnode = docutils.nodes.citation_reference(
        rawsource='[%s]_' % label,
        refname=refname)
    label_text = docutils.nodes.Text(label)
    refnode += label_text
    refnode['classes'].extend(classes)
    document.note_citation_ref(refnode)
    return refnode


def docutils_citation_node(entry, document, use_key_as_label=True,
                           convert_latex=True):
    """Return citation node, with key as name, label as first child,
    and nodes with entry text (converted from latex) as subsequent children.

    The citation is expected to be inserted into the *document*
    prior to any docutils transforms.
    """
    # see docutils.parsers.rst.states.Body.citation()
    if not isinstance(entry, BibGlossEntry):
        raise TypeError

    if use_key_as_label:
        label = entry.key
    else:
        label = entry.label
    name = docutils.nodes.fully_normalize_name(entry.key)

    citation = docutils.nodes.citation()
    citation['names'].append(name)
    citation += docutils.nodes.label('', label)
    if convert_latex:
        for child in latex_to_docutils(entry.text):
            citation += child
    else:
        citation += docutils.nodes.paragraph(
            '', '', docutils.nodes.Text(entry.text, entry.text))
    citation['classes'].append('bibglossary')
    document.note_citation(citation)
    document.note_explicit_target(citation, citation)
    return citation


def format_entries(entries, style='list', sort=True):
    # TODO apply styles consistent with latex glossaries
    if sort:
        entries = sorted(entries, key=lambda e: e.sortkey)
    labels = [e.label for e in entries]
    for label, entry in zip(labels, entries):
        yield entry


def rst_to_docutils(source):
    parser = docutils.parsers.rst.Parser()
    settings = docutils.frontend.OptionParser(
        components=(docutils.parsers.rst.Parser,)
    ).get_default_values()
    document = docutils.utils.new_document('dummy_source_path', settings)
    parser.parse(source, document)
    return document


def latex_to_docutils(source):
    import panflute as pf
    rst_source = pf.convert_text(
        source, input_format='latex', output_format='rst')
    return rst_to_docutils(rst_source)
