import io

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


def get_empty_bib():
    return bibtexparser.bibdatabase.BibDatabase()


class EntryObj(object):
    def __init__(self, entry_dict):
        self._entry_dict = entry_dict

    def _get_key(self):
        return self._entry_dict['ID']

    def _set_key(self, key):
        self._entry_dict['ID'] = key

    key = property(_get_key, _set_key)

    @property
    def type(self):
        return self._entry_dict['ENTRYTYPE']

    @property
    def label(self):
        if self.type == "acronym":
            return self._entry_dict['abbreviation']
        elif self.type == "glossaryterm":
            return self._entry_dict['name']
        else:
            raise NotImplementedError

    @property
    def plural(self):
        if 'plural' in self._entry_dict:
            return self._entry_dict['plural']
        else:
            return "{}s".format(self.label)

    @property
    def text(self):
        if self.type == "acronym":
            return self._entry_dict['longname']
        elif self.type == "glossaryterm":
            return self._entry_dict['description']
        else:
            raise NotImplementedError

    @property
    def fields(self):
        return self._entry_dict.copy()


def get_fake_entry_obj(key):
    return EntryObj({
        'ENTRYTYPE': 'glossaryterm',
        'ID': key,
        'name': key,
        'description': ''
    })


def get_entry_objects(bib):
    return [e if isinstance(e, EntryObj) else EntryObj(e) for e in bib.entries]


def parse_bib(text_str=None, path=None, bib=None, encoding="utf8"):
    """ parse bib file
    """
    if bib is not None and text_str is not None and path is None:
        raise ValueError("only one of text_str or bib must be supplied")
    if bib is not None:
        if not isinstance(bib, bibtexparser.bibdatabase.BibDatabase):
            raise ValueError("bib is not a BibDatabase instance")
        return bib
    elif path is not None:
        if text_str is not None:
            raise ValueError(
                'text_str and path cannot be set at the same time')
        with io.open(path, encoding=encoding) as fobj:
            text_str = fobj.read()
    parser = bibtexparser.bparser.BibTexParser()
    parser.ignore_nonstandard_types = False
    parser.encoding = encoding
    bib = parser.parse(text_str)
    # TODO doesn't appear to check for key duplication

    return bib
