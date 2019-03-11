import re
import sys
from textwrap import dedent
import pytest
from ipypublish.bib2glossary import BibGlossDB

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

tex_str = """\
    \\newacronym[description={a description}]{akey1}{OTHER}{Abbreviation of other}
    \\newglossaryentry{gtkey1}{
        name={other name},
        description={the description of other}
    }
    \\newglossaryentry{skey1}{
        name={name},
        description={the description},
        type={symbols}
    }
    """  # noqa: E501


def test_load_bib_type_error():

    bibgloss = BibGlossDB()
    with pytest.raises(TypeError):
        bibgloss.load_bib(
            text_str=dedent(bib_str), ignore_nongloss_types=False)


def test_load_bib_type_ignore():

    bibgloss = BibGlossDB()
    bibgloss.load_bib(text_str=dedent(bib_str), ignore_nongloss_types=True)
    assert set(bibgloss.keys()) == {
        'gtkey1', 'gtkey2', 'akey1', 'akey2', 'skey1'}


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_load_tex():

    bibgloss = BibGlossDB()
    bibgloss.load_tex(text_str=dedent(tex_str))
    assert {k: e.type for k, e in bibgloss.items()} == {
        'gtkey1': 'glsterm',
        'akey1': 'glsacronym',
        'skey1': 'glssymbol'}


def test_to_dict():
    bibgloss = BibGlossDB()
    bibgloss.load_bib(text_str=dedent(bib_str), ignore_nongloss_types=True)
    dct = bibgloss.to_dict()
    assert set(dct.keys()) == {
        'gtkey1', 'gtkey2', 'akey1', 'akey2', 'skey1'}


def test_to_bib_string():
    bibgloss = BibGlossDB()
    bibgloss.load_bib(text_str=dedent(bib_str), ignore_nongloss_types=True)
    string = bibgloss.to_bib_string()
    assert re.search(
        "@glsacronym\\{akey1,.*@glsterm\\{gtkey1,.*@glssymbol\\{skey1.*",
        string,
        re.DOTALL
    )


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
