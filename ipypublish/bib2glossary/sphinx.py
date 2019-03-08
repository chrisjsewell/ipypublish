import logging

import docutils

from ipypublish.bib2glossary.common import (
    parse_bib, DEFAULT_ACRONYM_P2F, DEFAULT_GLOSS_P2F,
    DEFAULT_GLOSS_ETYPE, DEFAULT_ACRONYM_ETYPE, EntryObj
)

logger = logging.getLogger(__name__)

# TODO see https://github.com/sphinx-doc/sphinx/issues/4298
# for possible acronym directive
# TODO add better directive for glossary (that better mirrors latex glossaries)


def bib_to_sphinx_glossary(text_str=None, bib=None,
                           sort_keys=True, filter_keys=None,
                           glossary_type=DEFAULT_GLOSS_ETYPE,
                           acronym_type=DEFAULT_ACRONYM_ETYPE):
    """Set docstring here.

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


def docutils_citation_reference_node(
        entry, document, use_key_as_label=True):
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
    refnode.set_class('bibglossary')
    # refnode.tagname = 'glossary_reference'
    document.note_citation_ref(refnode)
    return refnode


def docutils_entry_paragraph(entry):
    """Return a docutils.nodes.paragraph
    containing the rendered text for *entry* (without label).

    """
    if not isinstance(entry, EntryObj):
        entry = EntryObj(entry)
    return docutils.nodes.paragraph(
        '', '', docutils.nodes.Text(entry.text, entry.text))


def docutils_citation_node(entry, document, use_key_as_label=True):
    """Return citation node, with key as name, label as first
    child, and paragraph with entry text as second child. The citation is
    expected to be inserted into *document* prior to any docutils
    transforms.
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
    citation += docutils_entry_paragraph(entry)
    citation.set_class('bibglossary')
    document.note_citation(citation)
    document.note_explicit_target(citation, citation)
    return citation


class StyleEntries(object):

    def sort_entries(self, entries):
        return sorted(entries, key=lambda e: e.label)

    def format_labels(self, entries):
        return [e.label for e in entries]

    def format_entry(self, label, entry, bib_data=None):
        return entry

    def format_entries(self, entries, bib_data=None):
        sorted_entries = self.sort_entries(entries)
        labels = self.format_labels(sorted_entries)
        for label, entry in zip(labels, sorted_entries):
            yield self.format_entry(label, entry, bib_data=bib_data)
