import logging

from ipypublish.bib2glossary.common import (
    parse_bib, DEFAULT_ACRONYM_P2F, DEFAULT_GLOSS_P2F,
    DEFAULT_GLOSS_ETYPE, DEFAULT_ACRONYM_ETYPE
)

logger = logging.getLogger(__name__)


def bib_to_tex_glossterms(text_str=None, bib=None,
                          entry_type=DEFAULT_GLOSS_ETYPE,
                          param2field=None):
    """create a list of tex newglossaryentry strings

    Parameters
    ----------
    text_str: str or None
        the .bib file text to parse
    bib: None or object
        a bibtexparser.bibdatabase.BibDatabase instance
    entry_type: None or str
        if given, filter by entry_type
    param2field: None or dict
        mapping of glossaries parameter to bib field

    Returns
    -------
    list[str]:
        list of newglossaryentry

    """
    entries = parse_bib(text_str, bib).get_entry_dict()

    param2field_default = dict(DEFAULT_GLOSS_P2F)
    if param2field is not None:
        param2field_default.update(param2field)
    param2field = param2field_default.copy()

    assert "description" in param2field
    assert "name" in param2field
    name_field = param2field.get("name")
    descript_field = param2field.get("description")

    glossaries = []
    for key in sorted(entries.keys()):

        fields = entries.get(key)

        if entry_type and entry_type != (fields.get('ENTRYTYPE', '')):
            continue

        if name_field not in fields:
            logger.warn(
                "Skipping {0}: No {1} key found".format(key, name_field))
            continue
        if descript_field not in fields:
            logger.warn("Skipping {0}: No {1} key found".format(
                key, descript_field))
            continue

        options = []
        for param in sorted(param2field.keys()):
            field = param2field[param]
            if field in fields:
                options.append("{0}={{{1}}}".format(param, fields[field]))
        body = "{{{key}}}{{\n    {params}\n}}".format(
            key=key,
            params=",\n    ".join(options))

        glossaries.append("\\newglossaryentry"+body)

    return glossaries


def bib_to_tex_acronyms(text_str=None, bib=None,
                        entry_type=DEFAULT_ACRONYM_ETYPE,
                        param2field=None):
    """create a list of tex newacronym strings

    Parameters
    ----------
    text_str: str or None
        the .bib file text to parse
    bib: None or object
        a bibtexparser.bibdatabase.BibDatabase instance
    entry_type: None or str
        if given, filter by entry_type
    param2field: None or dict
        mapping of abbreviation parameter to bib field

    Returns
    -------
    list[str]
        list of acronyms

    """
    entries = parse_bib(text_str, bib).get_entry_dict()

    param2field_default = dict(DEFAULT_ACRONYM_P2F)
    if param2field is not None:
        param2field_default.update(param2field)
    param2field = param2field_default.copy()

    assert "abbreviation" in param2field
    assert "longname" in param2field
    abbrev_field = param2field.pop("abbreviation")
    name_field = param2field.pop("longname")

    acronyms = []
    for key in sorted(entries.keys()):

        fields = entries.get(key)

        if entry_type and entry_type != (fields.get('ENTRYTYPE', '')):
            continue

        if abbrev_field not in fields:
            logger.warn("Skipping {0}: No {1} key found".format(
                key, abbrev_field))
            continue
        if name_field not in fields:
            logger.warn(
                "Skipping {0}: No {1} key found".format(key, name_field))
            continue

        body = "{{{key}}}{{{abbreviation}}}{{{name}}}".format(
            key=key,
            abbreviation=fields[abbrev_field],
            name=fields[name_field])
        options = []
        for param in sorted(param2field.keys()):
            field = param2field[param]
            if field in fields:
                options.append("{0}={{{1}}}".format(param, fields[field]))
        if options:
            body = "[" + ",".join(options) + "]" + body

        acronyms.append("\\newacronym"+body)

    return acronyms
