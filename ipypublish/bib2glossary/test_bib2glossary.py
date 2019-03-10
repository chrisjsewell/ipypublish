from textwrap import dedent
from ipypublish.bib2glossary.latex import (
    bib_to_tex_glossterms, bib_to_tex_acronyms)


def test_bib_to_tex_glossary():

    input_str = """\
    @glossaryterm{thekey,
    description = {the description},
    name = {name}
    }
    @glossaryterm{otherkey,
    description = {the description of other},
    name = {other name}
    }
    """
    glossaries = bib_to_tex_glossterms(dedent(input_str))

    expected_str = """\
    \\newglossaryentry{otherkey}{
        description={the description of other},
        name={other name}
    }
    \\newglossaryentry{thekey}{
        description={the description},
        name={name}
    }"""

    assert "\n".join(glossaries) == dedent(expected_str)


def test_bib_to_tex_acronym():

    text_str = """\
    @acronym{thekey,
    abbreviation = {ABRV},
    longname = {Abbreviation}
    }
    @acronym{otherkey,
    abbreviation = {OTHER},
    longname = {Abbreviation of other}
    }
    """
    acronyms = bib_to_tex_acronyms(dedent(text_str))

    assert acronyms == [
        "\\newacronym{otherkey}{OTHER}{Abbreviation of other}",
        "\\newacronym{thekey}{ABRV}{Abbreviation}"]


def test_bib_to_tex_acronym_with_options():

    text_str = """\
    @acronym{thekey,
    abbreviation = {ABRV},
    longname = {Abbreviation},
    description = {a description}
    }
    @acronym{otherkey,
    abbreviation = {OTHER},
    longname = {Abbrev of other},
    plural = {OTHERs}
    }
    """
    acronyms = bib_to_tex_acronyms(dedent(text_str))

    assert acronyms == [
        "\\newacronym[plural={OTHERs}]{otherkey}{OTHER}{Abbrev of other}",
        "\\newacronym[description={a description}]{thekey}{ABRV}{Abbreviation}"
    ]
