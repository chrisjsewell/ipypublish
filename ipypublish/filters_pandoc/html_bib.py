import io
import re
import string

from six import string_types
import bibtexparser


def read_bibliography(path, raise_error=True):
    """ read a bibliography

    """
    bibdatabase = {}
    bibparser = bibtexparser.bparser.BibTexParser()
    try:
        if hasattr(path, 'open'):
            with path.open(encoding="utf8") as bibtex_file:
                bibtex_data = bibtex_file.read()
        else:
            with io.open(path, encoding="utf8") as bibtex_file:
                bibtex_data = bibtex_file.read()
        bibtex_data = safe_str(bibtex_data)
        bibdatabase = bibparser.parse(bibtex_data).entries_dict
    except Exception as err:
        if raise_error:
            raise IOError('could not read bibliopath {}: {}'.format(path, err))

    return bibdatabase


def process_bib_entry(cid, bibdatabase, bibnums,
                      fallback_fmt="[{author_abbrev}, {year}]"):
    """work out the best way to represent the bib entry """
    entry = bibdatabase[cid]
    if cid not in bibnums:
        bibnums[cid] = len(bibnums) + 1

    if 'doi' in entry:
        return r'<a href="https://doi.org/{doi}">{text}</a>'.format(
            doi=entry['doi'], text=bibnums[cid])
    elif 'url' in entry:
        return r'<a href="{url}">{text}</a>'.format(
            url=entry['url'], text=bibnums[cid])
    elif 'link' in entry:
        return r'<a href="{url}">{text}</a>'.format(
            url=entry['link'], text=bibnums[cid])
    else:
        return bibnums[cid]
        # add_abbreviated_author(entry)
        # split_date(entry)
        # return DefaultFormatter().format(fallback_fmt, **entry)


def add_abbreviated_author(entry):
    # abbreviate a list of authors
    if 'author' in entry:
        authors = re.split(", | and ", entry['author'])
        if len(authors) > 1:
            author_abbrev = authors[0] + ' <em>et al</em>'
        else:
            author_abbrev = authors[0]
        entry["author_abbrev"] = author_abbrev


def split_date(entry):
    # split up date into year, month, day
    if 'date' in entry:
        date = entry['date'].split('-')
        if len(date) == 3:
            entry['year'] = date[0]
            entry['month'] = date[1]
            entry['day'] = date[2]
        else:
            entry['year'] = date[0]


class DefaultFormatter(string.Formatter):
    def __init__(self, default=''):
        self.default = default

    def get_value(self, key, args, kwds):
        if isinstance(key, string_types):
            return kwds.get(key, self.default.format(key))
        else:
            string.Formatter.get_value(key, args, kwds)


def safe_str(obj):
    if hasattr(obj, "decode"):
        try:
            obj = obj.decode("utf-8")
        except UnicodeEncodeError:
            pass
    try:
        return str(obj)
    except UnicodeEncodeError:
        # python 2.7
        obj = re.sub(u"\u2013", "-", obj)   # en dash
        obj = re.sub(u"\u2014", "--", obj)  # em dash
        return obj.encode('ascii', 'ignore').decode('ascii')
    return ""
