import logging

from ipypublish.bib2glossary.shared import (
    parse_bib, DEFAULT_ACRONYM_P2F, DEFAULT_GLOSS_P2F,
    DEFAULT_GLOSS_ETYPE, DEFAULT_ACRONYM_ETYPE
)

logger = logging.getLogger(__name__)

# TODO see https://github.com/sphinx-doc/sphinx/issues/4298
# for possible acronym directive
# TODO add better directive for glossary (that better mirrors latex glossaries)


def bib_to_sphinx_glossary(text_str, sort_keys=True, filter_keys=None,
                           glossary_type=DEFAULT_GLOSS_ETYPE,
                           acronym_type=DEFAULT_ACRONYM_ETYPE):
    """Set docstring here.

    Parameters
    ----------
    text_str: str
        string representing bibtex file
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
    gparam2field = dict(DEFAULT_GLOSS_P2F)
    gname_field = gparam2field.get("name")
    gdescript_field = gparam2field.get("description")

    aparam2field = dict(DEFAULT_ACRONYM_P2F)
    abbrev_field = aparam2field.pop("abbreviation")
    alongname_field = aparam2field.get("longname")

    entries = parse_bib(text_str)

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
