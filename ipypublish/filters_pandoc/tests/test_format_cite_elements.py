from ipypublish.filters_pandoc.utils import apply_filter
from ipypublish.filters_pandoc import (prepare_cites,
                                       format_cite_elements)


def test_multiple_references_rst():
    """
    """
    in_string = [
       'multiple references +[@fig:id; @tbl:id; @eq:id1]'
    ]

    out_string = apply_filter(in_string,
                              [prepare_cites.main,
                               format_cite_elements.main], "rst")

    print(out_string)
    assert out_string == "\n".join([
        "multiple references :ref:`fig:id`, :ref:`tbl:id` and :ref:`eq:id1`"
    ])


def test_multiple_references_latex():
    """
    """
    in_string = [
       'multiple references +[@fig:id; @tbl:id; @eq:id1]'
    ]

    out_string = apply_filter(in_string,
                              [prepare_cites.main,
                               format_cite_elements.main], "latex")

    print(out_string)
    assert out_string == "\n".join([
        "multiple references \\cref{fig:id,tbl:id,eq:id1}"
    ])


def test_reference_prefixes_latex():
    """
    """
    in_string = [
       '(?@key1 &@key2 =@key3)'
    ]

    out_string = apply_filter(in_string,
                              [prepare_cites.main,
                               format_cite_elements.main], "latex")

    print(out_string)
    assert out_string == "\n".join([
        "(\\Cref{key1} \\gls{key2} \\eqref{key3})"
    ])


def test_reference_prefixes_rst():
    """
    """
    in_string = [
       '(?@key1 &@key2 %@key3 =@key4)'
    ]

    out_string = apply_filter(in_string,
                              [prepare_cites.main,
                               format_cite_elements.main], "rst")

    print(out_string)
    assert out_string == "\n".join([
        "(:ref:`key1` :gls:`key2` :glsc:`key3` :eq:`key4`)"
    ])
