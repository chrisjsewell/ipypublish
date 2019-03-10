import logging

import docutils
import panflute as pf

from ipypublish.bib2glossary.common import (
    parse_bib, DEFAULT_ACRONYM_P2F, DEFAULT_GLOSS_P2F,
    DEFAULT_GLOSS_ETYPE, DEFAULT_ACRONYM_ETYPE, EntryObj
)

logger = logging.getLogger(__name__)

# TODO advertise extension at https://github.com/sphinx-doc/sphinx/issues/4298


def bib_to_sphinx_glossary(text_str=None, bib=None,
                           sort_keys=True, filter_keys=None,
                           glossary_type=DEFAULT_GLOSS_ETYPE,
                           acronym_type=DEFAULT_ACRONYM_ETYPE):
    """create a standard sphinx glossary from a bib file

    Parameters
    ----------
    text_str: str or None
        the .bib file text to parse
    bib: None or object
        a bibtexparser.bibdatabase.BibDatabase instance
    sort_keys=True: bool
        add :sorted: option to directive
    filter_keys=None: None or list[str]
        if not None, only output keys defined in this list
    glossary_type: str
        the entry_type for glossary terms
    acronym_type: str
        the entry_type for acronyms

    Returns
    -------
    list[str]

    """
    entries = parse_bib(text_str, bib).get_entry_dict()

    gparam2field = dict(DEFAULT_GLOSS_P2F)
    gname_field = gparam2field.get("name")
    gdescript_field = gparam2field.get("description")

    aparam2field = dict(DEFAULT_ACRONYM_P2F)
    abbrev_field = aparam2field.pop("abbreviation")
    alongname_field = aparam2field.get("longname")

    glossary_str = [
        ".. glossary::",
    ]
    if sort_keys:
        glossary_str.append("   :sorted:")
    glossary_str.append("")

    for key in sorted(entries.keys()):

        if filter_keys is not None and key not in filter_keys:
            continue

        fields = entries.get(key)

        if (fields.get('ENTRYTYPE', '')) == glossary_type:

            if gname_field not in fields:
                logger.warn(
                    "Skipping {0}: No {1} key found".format(key, gname_field))
                continue
            if gdescript_field not in fields:
                logger.warn("Skipping {0}: No {1} key found".format(
                    key, gdescript_field))
                continue

            glossary_str.append("   {}".format(key))
            glossary_str.append("      [{}]".format(fields[gname_field]))
            # indent all lines correctly
            glossary_str.extend(
                [" " * 6 + l.strip()
                 for l in fields[gdescript_field].splitlines()])
            glossary_str.append("")

        elif (fields.get('ENTRYTYPE', '')) == acronym_type:

            if alongname_field not in fields:
                logger.warn(
                    "Skipping {0}: No {1} key found".format(
                        key, alongname_field))
                continue
            if abbrev_field not in fields:
                logger.warn("Skipping {0}: No {1} key found".format(
                    key, abbrev_field))
                continue

            glossary_str.append("   {}".format(key))
            glossary_str.append("      [{}]".format(fields[abbrev_field]))
            # indent all lines correctly
            glossary_str.extend(
                [" " * 6 + l.strip()
                 for l in fields[alongname_field].splitlines()])
            glossary_str.append("")

    return glossary_str


def docutils_citation_ref_node(
        entry, document, use_key_as_label=True, classes=('bibglossary',)):
    # type: (dict, docutils.nodes.document, bool) -> docutils.nodes.citation_reference  # noqa
    """Return citation_reference node to the given citation. The
    citation_reference is expected to be inserted into *document*
    prior to any docutils transforms.
    """
    if not isinstance(entry, EntryObj):
        entry = EntryObj(entry)
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


def docutils_citation_node(entry, document, use_key_as_label=True):
    """Return citation node, with key as name, label as first child,
    and nodes with entry text (converted from latex) as subsequent children.

    The citation is expected to be inserted into the *document*
    prior to any docutils transforms.
    """
    # see docutils.parsers.rst.states.Body.citation()
    if not isinstance(entry, EntryObj):
        entry = EntryObj(entry)

    if use_key_as_label:
        label = entry.key
    else:
        label = entry.label
    name = docutils.nodes.fully_normalize_name(entry.key)

    citation = docutils.nodes.citation()
    citation['names'].append(name)
    citation += docutils.nodes.label('', label)
    for child in latex_to_docutils(entry.text):
        citation += child
    # citation += docutils_entry_paragraph(entry)
    citation['classes'].append('bibglossary')
    document.note_citation(citation)
    document.note_explicit_target(citation, citation)
    return citation


def format_entries(entries, style='list', sort=True):
    # TODO apply styles consistent with latex glossaries
    if sort:
        entries = sorted(entries, key=lambda e: e.label.lower())
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
    rst_source = pf.convert_text(
        source, input_format='latex', output_format='rst')
    return rst_to_docutils(rst_source)
