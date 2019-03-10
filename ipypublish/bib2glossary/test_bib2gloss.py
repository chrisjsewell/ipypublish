from textwrap import dedent
import pytest
from ipypublish.bib2glossary.common import BibGlossDB

bib_str = """\
    @glsterm{gtkey1,
    description = {the description},
    name = {name}
    }
    @glsterm{gtkey2,
    description = {the description of other},
    name = {other name}
    }
    @glsacronym{akey1,
    abbreviation = {ABRV},
    longname = {Abbreviation},
    description = {a description}
    }
    @glsacronym{akey2,
    abbreviation = {OTHER},
    longname = {Abbrev of other},
    plural = {OTHERs}
    }
    @glssymbol{skey1,
    description = {the description of symbol},
    name = {\\pi}
    }
    @badtype{bkey1,
    field = {text}
    }
    """

# TODO check for key duplication
# see https://github.com/sciunto-org/python-bibtexparser/issues/237


def test_load_bib_type_error():

    bibgloss = BibGlossDB()
    with pytest.raises(TypeError):
        bibgloss.load_bib(
            text_str=dedent(bib_str), ignore_nongloss_types=False)


def test_load_bib_type_ignore():

    bibgloss = BibGlossDB()
    bibgloss.load_bib(text_str=dedent(bib_str), ignore_nongloss_types=True)
    assert list(bibgloss.keys()) == [
        'gtkey1', 'gtkey2', 'akey1', 'akey2', 'skey1']


def test_to_latex_dict():
    bibgloss = BibGlossDB()
    bibgloss.load_bib(text_str=dedent(bib_str), ignore_nongloss_types=True)
    latex_dict = bibgloss.to_latex_dict()
    print(latex_dict)
    assert latex_dict == {
        ('glsacronym',
            'akey1'): [(
                '\\newacronym[description={a description}]{'
                'akey1}{ABRV}{Abbreviation}')],
        ('glsacronym',
         'akey2'): [(
             '\\newacronym[plural={OTHERs}]{'
             'akey2}{OTHER}{Abbrev of other}')],
        ('glsterm',
            'gtkey1'): [
            '\\newglossaryentry{gtkey1}{',
            '    description={the description},',
            '    name={name}',
            '}'],
        ('glsterm',
            'gtkey2'): [
            '\\newglossaryentry{gtkey2}{',
            '    description={the description of other},',
            '    name={other name}',
            '}'],
        ('glssymbol',
         'skey1'): [
            '\\newglossaryentry{skey1}{',
            '    description={the description of symbol},',
            '    name={\\pi},',
            '    type={symbols}',
            '}']
    }
