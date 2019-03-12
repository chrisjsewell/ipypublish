import copy
import io
import logging
import os

import bibtexparser

from ipypublish.bib2glossary.definitions import (
    ETYPE_GLOSS, ETYPE_ACRONYM, ETYPE_SYMBOL,
    NEWGLOSS_FIELDS, NEWACRONYM_FIELDS
)

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

logger = logging.getLogger(__name__)


class BibGlossEntry(object):
    _allowed_types = (
        ETYPE_GLOSS, ETYPE_ACRONYM, ETYPE_SYMBOL
    )

    def __init__(self, entry_dict):

        self._validate_dict(entry_dict)
        self._entry_dict = entry_dict

    def _validate_dict(self, dct):
        if 'ID' not in dct:
            raise KeyError
        if 'ENTRYTYPE' not in dct:
            raise KeyError

        if dct['ENTRYTYPE'] not in self._allowed_types:
            raise TypeError(
                'ENTRYTYPE must be one of: {}'.format(self._allowed_types))

        if dct['ENTRYTYPE'] == ETYPE_ACRONYM:
            if 'abbreviation' not in dct or 'longname' not in dct:
                raise KeyError
        elif (dct['ENTRYTYPE'] == ETYPE_GLOSS
              or dct['ENTRYTYPE'] == ETYPE_SYMBOL):
            if 'name' not in dct or 'description' not in dct:
                raise KeyError

    def _get_key(self):
        return self._entry_dict['ID']

    def _set_key(self, key):
        self._entry_dict['ID'] = key

    key = property(_get_key, _set_key)

    @property
    def type(self):
        return self._entry_dict['ENTRYTYPE']

    def __contains__(self, key):
        return key in self._entry_dict

    def get(self, key):
        return self._entry_dict[key]

    @property
    def label(self):
        if self.type == ETYPE_ACRONYM:
            return self.get('abbreviation')
        elif self.type == ETYPE_GLOSS:
            return self.get('name')
        elif self.type == ETYPE_SYMBOL:
            return self.get('name')
        else:
            raise NotImplementedError

    @property
    def sortkey(self):
        if "sort" in self:
            return self.get("sort")
        else:
            return self.label.lower()

    @property
    def plural(self):
        if 'plural' in self:
            return self.get('plural')
        else:
            return "{}s".format(self.label)

    @property
    def text(self):
        if self.type == ETYPE_ACRONYM:
            return self.get('longname')
        elif self.type == ETYPE_GLOSS:
            return self.get('description')
        elif self.type == ETYPE_SYMBOL:
            return self.get('description')
        else:
            raise NotImplementedError

    def __repr__(self):
        return "BibGlossEntry(key={0},label={1})".format(self.key, self.label)

    def to_dict(self):
        return copy.deepcopy(self._entry_dict)

    def to_latex(self):

        if self.type in [ETYPE_GLOSS, ETYPE_SYMBOL]:
            options = []
            for field in sorted(NEWGLOSS_FIELDS):
                if field in self:
                    options.append("{0}={{{1}}}".format(
                        field, self.get(field)))
            if self.type == ETYPE_SYMBOL:
                options.append("type={symbols}")
            body = "{{{key}}}{{\n    {options}\n}}".format(
                key=self.key, options=",\n    ".join(options))
            return "\\newglossaryentry" + body

        elif self.type == ETYPE_ACRONYM:
            body = "{{{key}}}{{{abbrev}}}{{{long}}}".format(
                key=self.key, abbrev=self.label, long=self.text)
            options = []
            for field in sorted(NEWACRONYM_FIELDS):
                if field in self:
                    options.append("{0}={{{1}}}".format(
                        field, self.get(field)))
            if options:
                body = "[" + ",".join(options) + "]" + body

            return "\\newacronym" + body


class BibGlossDB(MutableMapping):

    def __init__(self):
        self._entries = {}

    def __getitem__(self, key):
        return self._entries[key]

    def __setitem__(self, key, entry):
        if not isinstance(entry, BibGlossEntry):
            raise ValueError('value must be a BibGlossEntry')
        if key != entry.key:
            raise ValueError('key must equal entry.key')
        self._entries[key] = entry

    def __delitem__(self, key):
        del self._entries[key]

    def __iter__(self):
        return iter(self._entries)

    def __len__(self):
        return len(self._entries)

    @staticmethod
    def get_fake_entry_obj(key):
        return BibGlossEntry({
            'ENTRYTYPE': ETYPE_GLOSS,
            'ID': key,
            'name': key,
            'description': ''
        })

    def load_bib(self, text_str=None, path=None, bibdb=None, encoding="utf8",
                 ignore_nongloss_types=False,
                 ignore_duplicates=False):
        """load a bib file

        Parameters
        ----------
        text_str=None: str or None
            string representing the bib file contents
        path=None: str or None
            path to bibfile
        bibdb=None: bibtexparser.bibdatabase.BibDatabase or None
        encoding="utf8": str
            bib file encoding
        ignore_nongloss_types: bool
            if False, a KeyError will be raised for non-gloss types
        ignore_duplicates: bool
            if False, a KeyError will be raised if multiple entries are found
            with the same key, otherwise only the first entry will be used

        """
        bib = None

        if sum([e is not None for e in [text_str, path, bibdb]]) != 1:
            raise ValueError(
                "only one of text_str, path or bib must be supplied")
        if bibdb is not None:
            if not isinstance(bibdb, bibtexparser.bibdatabase.BibDatabase):
                raise ValueError("bib is not a BibDatabase instance")
            bib = bibdb
        elif path is not None:
            if text_str is not None:
                raise ValueError(
                    'text_str and path cannot be set at the same time')
            with io.open(path, encoding=encoding) as fobj:
                text_str = fobj.read()

        if bib is None:
            parser = bibtexparser.bparser.BibTexParser()
            parser.ignore_nonstandard_types = False
            parser.encoding = encoding
            bib = parser.parse(text_str)
            # TODO doesn't appear to check for key duplication
            # see https://github.com/sciunto-org/python-bibtexparser/issues/237

        entries = {}
        for entry_dict in bib.entries:

            try:
                entry = BibGlossEntry(entry_dict)
            except TypeError:
                if ignore_nongloss_types:
                    logger.warning('Skipping non-glossary entry')
                    continue
                else:
                    raise

            if entry.key in entries:
                if ignore_duplicates:
                    logger.warning('Skipping duplicate key entry')
                    continue
                else:
                    raise KeyError(
                        "the bib file contains "
                        "multiple entries with the key: {}".format(entry.key))

            entries[entry.key] = entry

        # self._bib = bib
        self._entries = entries

        return True

    def load_tex(self, text_str=None, path=None, encoding='utf8',
                 skip_ioerrors=False, ignore_unknown_types=True):
        """load a tex file

        Parameters
        ----------
        text_str=None: str or None
            string representing the bib file contents
        path=None: str or None
            path to bibfile
        bibdb=None: bibtexparser.bibdatabase.BibDatabase or None
        encoding="utf8": str
            bib file encoding
        skip_ioerrors: bool
            if False, an IOError will be raised if
            newglossaryterm or newacronym is badly formatted
        ignore_unknown_types: bool
            if True, strip unknown types, otherwise raise a ValueError

        Notes
        -----
        the texsoup package is required.

        if a newglossaryterm has field 'type={symbols}', then
        it will be loaded as a symbol

        """
        from ipypublish.bib2glossary.parse_tex import parse_tex
        gterms, acronyms = parse_tex(
            text_str=text_str, path=path, encoding=encoding,
            skip_ioerrors=skip_ioerrors
        )
        entries = {}
        for key, fields in gterms.items():

            fields["ENTRYTYPE"] = ETYPE_GLOSS
            if fields.get("type", None) == "symbols":
                fields["ENTRYTYPE"] = ETYPE_SYMBOL
                fields.pop("type")
            elif "type" in fields:
                if not ignore_unknown_types:
                    raise ValueError("the 'type' is not recognised: "
                                     "{}".format(fields['type']))
                fields.pop("type")

            fields["ID"] = key
            entry = BibGlossEntry(fields)
            entries[entry.key] = entry

        for key, fields in acronyms.items():
            fields["ENTRYTYPE"] = ETYPE_ACRONYM
            fields["ID"] = key
            entry = BibGlossEntry(fields)
            entries[entry.key] = entry

        self._entries = entries

        return True

    @staticmethod
    def guess_path(path):
        """ guess the path of a bib file, with or without a file extension,
        from the available files in the path folder
        """
        basepath, extension = os.path.splitext(str(path))
        if extension in [".bib", ".biblatex", ".bibtex"]:
            return path
        elif extension in [".tex", ".latex"]:
            return path
        elif os.path.exists(basepath + ".bib"):
            return basepath + ".bib"
        elif os.path.exists(basepath + ".bibtex"):
            return basepath + ".bibtex"
        elif os.path.exists(basepath + ".biblatex"):
            return basepath + ".biblatex"
        elif os.path.exists(basepath + ".tex"):
            return basepath + ".tex"
        elif os.path.exists(basepath + ".latex"):
            return basepath + ".latex"
        else:
            return None

    def load(self, path, encoding='utf8'):
        """load a file, the type will be guessed from the extension,
        or (if no extension is given), the available files in the path folder

        Parameters
        ----------
        path: str
        encoding='utf8': str
            encoding of the file

        """
        path = self.guess_path(path)
        if path is None:
            raise IOError(
                "no acceptable loader found for path: {}".format(path))
        basepath, extension = os.path.splitext(str(path))
        if extension in [".bib", ".biblatex", ".bibtex"]:
            self.load_bib(path=path, encoding=encoding)
        elif extension in [".tex", ".latex"]:
            self.load_tex(path=path, encoding=encoding)

    def to_dict(self):
        return {k: e.to_dict() for k, e in self.items()}

    def to_bib_string(self):
        bibdb = bibtexparser.bibdatabase.BibDatabase()
        bibdb.entries = [e.to_dict() for e in self.values()]
        writer = bibtexparser.bwriter.BibTexWriter()
        writer.contents = ['comments', 'entries']
        writer.indent = '  '
        # writer.order_entries_by = ('ENTRYTYPE', 'ID')
        return writer.write(bibdb)

    def to_latex_dict(self, splitlines=True):
        """convert to dict of latex strings

        Returns
        -------
        dict:
            {(<type>, <key>): <latex string>}

        """
        latex_stings = {}
        for entry in self.values():
            string = entry.to_latex()
            if splitlines:
                string = string.splitlines()
            latex_stings[
                (entry.type, entry.key)] = string
        return latex_stings

    def to_latex_string(self):
        lines = []
        latex_dict = self.to_latex_dict(splitlines=False)
        for key in sorted(list(latex_dict.keys())):
            lines.append(latex_dict[key])
        return "\n".join(lines)
