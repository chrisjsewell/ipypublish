import bibtexparser

DEFAULT_GLOSS_ETYPE = 'glossaryterm'

DEFAULT_GLOSS_P2F = (("name", "name"),
                     ("description", "description"),
                     ("plural", "plural"),
                     ("symbol", "symbol"),
                     ("text", "text"),
                     ("sort", "sort"))

DEFAULT_ACRONYM_ETYPE = 'acronym'

DEFAULT_ACRONYM_P2F = (("abbreviation", "abbreviation"),
                       ("longname", "longname"),
                       ("description", "description"),
                       ("plural", "plural"),
                       ("longplural", "longplural"),
                       ("firstplural", "firstplural"))


def parse_bib(text_str):
    parser = bibtexparser.bparser.BibTexParser()
    parser.ignore_nonstandard_types = False
    bib = parser.parse(text_str)
    # TODO doesn't appear to check for key duplication
    entries = bib.get_entry_dict()
    return entries
