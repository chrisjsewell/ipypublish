import sys
import pytest

if sys.version_info >= (3, 0):
    from ipypublish.bib2glossary.parse_tex import parse_tex


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_parse_acronyms():

    text_str = """
    \\newacronym{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym{thekey}{ABRV}{Abbreviation}
    """
    gterms, acronyms = parse_tex(text_str=text_str)
    assert gterms == {}
    assert acronyms == {
        'otherkey': {
            'abbreviation': 'OTHER',
            'longname': 'Abbreviation of other'},
        'thekey': {
            'abbreviation': 'ABRV',
            'longname': 'Abbreviation'}
    }


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_parse_acronyms_with_options():

    text_str = """
    \\newacronym[description={a description}]{otherkey}{OTHER}{Abbreviation of other}
    \\newacronym[plural={ABRVs},longplural={Abbreviations}]{thekey}{ABRV}{Abbreviation}
    """  # noqa: E501
    gterms, acronyms = parse_tex(text_str=text_str)
    assert gterms == {}
    assert acronyms == {
        'otherkey': {
            'abbreviation': 'OTHER',
            'longname': 'Abbreviation of other',
            'description': 'a description'},
        'thekey': {
            'abbreviation': 'ABRV',
            'longname': 'Abbreviation',
            'longplural': 'Abbreviations',
            'plural': 'ABRVs'}
    }


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_parse_gterms():

    text_str = """
    \\newglossaryentry{otherkey}{
        name={other name},
        description={the description of other}
    }
    \\newglossaryentry{thekey}{
        name={name},
        description={the description},
        type={symbols}
    }
    """
    gterms, acronyms = parse_tex(text_str=text_str)
    assert acronyms == {}
    assert gterms == {
        'otherkey': {
            'description': 'the description of other',
            'name': 'other name'},
        'thekey': {
            'description': 'the description',
            'name': 'name',
            'type': 'symbols'}
    }


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_parse_mixed():
    text_str = """
    \\newacronym{otherkey}{OTHER}{Abbreviation of other}
    \\newglossaryentry{thekey}{
        name={name},
        description={the description},
        type={symbols}
    }
    """
    gterms, acronyms = parse_tex(text_str=text_str)
    assert acronyms == {
        'otherkey': {
            'abbreviation': 'OTHER',
            'longname': 'Abbreviation of other'}
    }
    assert gterms == {
        'thekey': {
            'description': 'the description',
            'name': 'name',
            'type': 'symbols'}
    }


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_duplicate_key():
    text_str = """
    \\newacronym{thekey}{OTHER}{Abbreviation of other}
    \\newglossaryentry{thekey}{
        name={name},
        description={the description},
        type={symbols}
    }
    """
    with pytest.raises(KeyError):
        parse_tex(text_str=text_str)


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_acronym_ioerror():
    text_str = """
    \\newacronym{thekey}{Abbreviation of other}
    """
    with pytest.raises(IOError):
        parse_tex(text_str=text_str)


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_gterm_ioerror():
    text_str = """
    \\newglossaryentry{}
    """
    with pytest.raises(IOError):
        parse_tex(text_str=text_str)


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="SyntaxError on import of texsoup/data.py line 135")
def test_ioerror_skip():
    text_str = """
    \\newacronym{thekey}{Abbreviation of other}
    \\newacronym{thekey2}{ABBR}{Abbreviation of other}
    """
    gterms, acronyms = parse_tex(text_str=text_str, skip_ioerrors=True)
    assert gterms == {}
    assert acronyms == {
        "thekey2": {
            'abbreviation': 'ABBR',
            'longname': 'Abbreviation of other'
        }
    }
