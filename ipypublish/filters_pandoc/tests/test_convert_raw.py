from ipypublish.filters_pandoc.utils import apply_filter
from ipypublish.filters_pandoc import (prepare_raw,
                                       format_cite_elements,
                                       format_raw_spans)


def test_mkdown_hlink_to_rst():
    out_string = apply_filter(
        "[a link](https://pandoc.org/filters.html)", [], "rst")
    assert out_string == "`a link <https://pandoc.org/filters.html>`__"


def test_latex_to_rst():
    """
    """
    in_string = [
        r"\cref{label1} \Cref{label2}  \cite{a-cite-key_2019}",
        "",
        "\\cite{label1,label2}",
        "",
        r"\ref{label3}  \todo{something todo}",
        "",
        r"\todo{something else todo}"
    ]

    out_string = apply_filter(in_string,
                              [prepare_raw.main,
                               format_cite_elements.main,
                               format_raw_spans.main], "rst")

    assert out_string == "\n".join([
        ":ref:`label1` :ref:`label2` :cite:`a-cite-key_2019`",
        "",
        ":cite:`label1,label2`",
        "",
        ":ref:`label3`",
        "",
        ".. todo:: something todo",
        "",
        "",
        "",
        ".. todo:: something else todo",
        "",
        ""
    ])


def test_latex_to_rst_with_numref():
    """"""
    in_string = [
        "---",
        "ipub:",
        "  pandoc:",
        "    use_numref: true",
        "---",
        "",
        r"\cref{label1} \Cref{label2}  \cite{a-cite-key_2019}",
        "",
        r"\ref{label3}  \todo[inline]{something todo}",
        "",
        r"\todo{something else todo}"
    ]

    out_string = apply_filter(in_string,
                              [prepare_raw.main,
                               format_cite_elements.main,
                               format_raw_spans.main], "rst")

    assert out_string.strip() == "\n".join([
        ":numref:`label1` :numref:`label2` :cite:`a-cite-key_2019`",
        "",
        ":ref:`label3`",
        "",
        ".. todo:: something todo"
        "",
        "",
        "",
        "",
        ".. todo:: something else todo"
    ])


def test_html_to_latex_label():

    in_string = [
        "[some text](#alabel)"
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "latex")

    assert out_string == "\n".join([
        r"\cref{alabel}"
    ])


def test_cite_in_table_caption():

    in_string = [
        'a b',
        '- -',
        '1 2',
        '',
        'Table: Caption \\cite{a}'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "markdown")

    assert out_string == "\n".join([
        '  a   b',
        '  --- ---',
        '  1   2',
        '',
        '  : Caption [@a]'
        ])


def test_html_to_latex_cite():

    in_string = [
        'surrounding <cite data-cite="cite_key">text</cite> text'
        "",
        '<cite data-cite="cite_key2"></cite>'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "latex")

    assert out_string == "\n".join([
        r"surrounding \cite{cite_key} text \cite{cite_key2}"
    ])


def test_html_to_rst_cite():

    in_string = [
        'surrounding <cite data-cite="cite_key">text</cite> text',
        "",
        '<cite data-cite="cite_key2"></cite>'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "rst")

    assert out_string == "\n".join([
        "surrounding :cite:`cite_key` text",
        "",
        ":cite:`cite_key2`"
    ])


def test_citations_latex():

    in_string = [
        '@label1',
        '',
        '[@label1;@label2]',
        '',
        '[an internal link](#label2)'
        '',
        '[an external link](http://something.org)',
        '',
        '![a citation @label](path/to/image.png)',
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "latex")

    assert out_string.strip() == "\n".join([
        "\\cite{label1}",
        "",
        "\\cite{label1,label2}",
        "",
        "\\cref{label2} \\href{http://something.org}{an external link}",
        "",
        "\\begin{figure}",
        "\\centering",
        "\\includegraphics{path/to/image.png}",
        "\\caption{a citation \\cite{label}}",
        "\\end{figure}"
    ])


def test_citations_rst():

    in_string = [
        '@label1',
        '',
        '[an internal link](#label2)'
        '',
        '[an external link](http://something.org)',
        '',
        '![a citation @label](path/to/image.png)',

    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "rst")

    assert out_string.strip() == "\n".join([
        ":cite:`label1`",
        "",
        ":ref:`label2` `an external link <http://something.org>`__",
        "",
        ".. figure:: path/to/image.png",
        "   :alt: a citation :cite:`label`",
        "",
        "   a citation :cite:`label`"
    ])


def test_rst_cite_to_rst():

    in_string = [
        'a :ref:`label` b'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "rst")

    assert out_string.strip() == "\n".join([
        'a :ref:`label` b'
    ])


def test_rst_cite_to_latex():

    in_string = [
        'a :ref:`label` b'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_cite_elements.main], "latex")

    assert out_string.strip() == "\n".join([
        r'a \ref{label} b'
    ])


def test_rst_known_role_to_rst():

    in_string = [
        'a :py:func:`label` b'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_raw_spans.main], "rst")

    assert out_string.strip() == "\n".join([
        'a :py:func:`label` b'
    ])


def test_rst_directive_to_rst():

    in_string = [
        '.. versionchanged:: v0.8.3',
        '',
        '    abc',
        '',
        '    xyz'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_raw_spans.main], "rst")

    assert out_string.strip() == "\n".join([
        '.. versionchanged:: v0.8.3',
        '',
        '    abc',
        '',
        '    xyz'
    ])


def test_rst_directive_to_latex():
    in_string = [
        '.. versionchanged:: v0.8.3',
        '',
        '    abc',
        '',
        '    xyz'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_raw_spans.main], "latex")

    assert out_string.strip() == "\n".join([
        '\\begin{mdframed}[frametitle={versionchanged},frametitlerule=true]',
        '\\mdfsubtitle{v0.8.3}',
        '',
        'abc',
        '',
        'xyz',
        '',
        '\\end{mdframed}',
        ])


def test_rst_directive_with_options_to_rst():

    in_string = [
        '.. dir::',
        '    :maxdepth: 2',
        '    :numbered:',
        '',
        '    abc',
        '    xyz',
        '',
        '    new paragraph',
        ''
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_raw_spans.main], "rst")

    assert out_string == "\n".join([
        '.. dir::',
        '    :maxdepth: 2',
        '    :numbered:',
        '',
        '    abc',
        '    xyz',
        '',
        '    new paragraph',
        "",
        ""
    ])


def test_rst_label_to_rst():

    in_string = [
        '.. _alabel:'
    ]

    out_string = apply_filter(
        in_string,
        [prepare_raw.main, format_raw_spans.main], "rst")

    assert out_string.strip() == "\n".join([
        '.. _alabel:'
    ])
