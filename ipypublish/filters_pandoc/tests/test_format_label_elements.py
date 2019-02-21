import pytest
from ipypublish.filters_pandoc.utils import apply_filter
from ipypublish.filters_pandoc import prepare_labels
from ipypublish.filters_pandoc import format_label_elements


def test_math_span_latex():

    in_json = {"blocks": [{"t": "Para", "c": [
        {"t": "Span", "c": [
            ["a", ["labelled-Math"], [["b", "2"]]],
            [{"t": "Math", "c": [{"t": "DisplayMath"}, "a=1"]}]]}
    ]}], "pandoc-api-version": [1, 17, 5, 1],
        "meta": {
        "$$references": {"t": "MetaMap", "c": {
            "a": {"t": "MetaMap", "c": {
                "type": {"t": "MetaString", "c": "Math"},
                "number": {"t": "MetaString", "c": "1"}}}}}}}

    out_string = apply_filter(
        in_json, format_label_elements.main, "latex", in_format="json")

    assert out_string.strip() == "\n".join([
        r"\begin{equation}a=1\label{a}\end{equation}"
    ])


def test_math_span_rst():

    in_json = {"blocks": [{"t": "Para", "c": [
        {"t": "Span", "c": [
            ["a", ["labelled-Math"], [["b", "2"]]],
            [{"t": "Math", "c": [{"t": "DisplayMath"}, "a=1"]}]]}
    ]}], "pandoc-api-version": [1, 17, 5, 1],
        "meta": {
        "$$references": {"t": "MetaMap", "c": {
            "a": {"t": "MetaMap", "c": {
                "type": {"t": "MetaString", "c": "Math"},
                "number": {"t": "MetaString", "c": "1"}}}}}}}

    out_string = apply_filter(
        in_json, format_label_elements.main, "rst", in_format="json")

    assert out_string.strip() == "\n".join([
        ".. math::",
        "   :nowrap:",
        "   :label: a",
        "",
        r"   \begin{equation}a=1\end{equation}"
    ])


@pytest.mark.skip(
    reason="there's an issue with pandoc outputting unicode in '/em> = 1'")
def test_math_span_html():

    in_json = {"blocks": [{"t": "Para", "c": [
        {"t": "Span", "c": [
            ["a", ["labelled-Math"], [["b", "2"]]],
            [{"t": "Math", "c": [{"t": "DisplayMath"}, "a=1"]}]]}
    ]}], "pandoc-api-version": [1, 17, 5, 1],
        "meta": {
        "$$references": {"t": "MetaMap", "c": {
            "a": {"t": "MetaMap", "c": {
                "type": {"t": "MetaString", "c": "Math"},
                "number": {"t": "MetaString", "c": "1"}}}}}}}

    out_string = apply_filter(
        in_json, format_label_elements.main, "html", in_format="json")

    assert out_string.strip() == "\n".join([
        '<p><a id="a" class="anchor-link" name="#a">'
        '<br />'
        '<span class="math display"><em>a</em> = 1</span>'
        '<br />'
        '</a></p>'
    ])


def test_math_md_to_rst():

    in_str = [
        "$$a = b$$ {#eq:id1}",
        "$$c &= d \\\\ other &= e$$ {#a env=align .unnumbered}"
    ]
    out_string = apply_filter(
        in_str, [prepare_labels.main, format_label_elements.main],
        in_format="markdown", out_format="rst")

    assert out_string.strip() == "\n".join([
        ".. math::",
        "   :nowrap:",
        "   :label: eq:id1",
        "",
        r"   \begin{equation}a = b\end{equation}",
        "",
        "",
        "",
        ".. math::",
        "   :nowrap:",
        "   :label: a",
        "",
        r"   \begin{align*}c &= d \\ other &= e\end{align*}"
    ])


def test_image_html():
    """
    """
    #  "![a title](path/to/image.png){#label1 .class-name a=5}"
    in_json = (
        {"blocks": [
            {"t": "Para", "c": [
                {"t": "Image", "c": [
                    ["label1",
                     ["class-name"],
                     [["a", "5"]]],
                    [{"t": "Str", "c": "a"},
                     {"t": "Space"}, {"t": "Str", "c": "title"}],
                    ["path/to/image.png", "fig:"]]}]}],
         "pandoc-api-version": [1, 17, 5, 1], "meta": {}}
    )

    out_string = apply_filter(
        in_json, format_label_elements.main, "html", in_format="json")

    assert out_string.strip() == "\n".join([
        '<p><a id="label1" class="anchor-link" name="#label1">'
        '<img src="path/to/image.png" title="fig:" alt="a title" id="label1" '
        'class="class-name" data-a="5" />'
        '</a></p>'
    ])


def test_image_rst():
    """
    """
    #  "![a title](path/to/image.png){#label1 .class-name a=5}"
    in_json = (
        {"blocks": [
            {"t": "Para", "c": [
                {"t": "Image", "c": [
                    ["label1",
                     ["class-name"],
                     [["a", "5"]]],
                    [{"t": "Str", "c": "a"},
                     {"t": "Space"}, {"t": "Str", "c": "title"}],
                    ["path/to/image.png", "fig:"]]}]}],
         "pandoc-api-version": [1, 17, 5, 1], "meta": {}}
    )

    out_string = apply_filter(
        in_json, format_label_elements.main, "rst", in_format="json")

    assert out_string.strip() == "\n".join([
        ".. figure:: path/to/image.png",
        "   :alt: a title",
        "   :figclass: class-name",
        "   :name: label1",
        "",
        "   a title"
    ])


def test_image_latex():
    """
    """
    #  "![a title](path/to/image.png){#label1 .class-name a=5}"
    in_json = (
        {"blocks": [
            {"t": "Para", "c": [
                {"t": "Image", "c": [
                    ["label1",
                     ["class-name"],
                     [["a", "5"]]],
                    [{"t": "Str", "c": "a"},
                     {"t": "Space"}, {"t": "Str", "c": "title"}],
                    ["path/to/image.png", "fig:"]]}]}],
         "pandoc-api-version": [1, 17, 5, 1], "meta": {}}
    )

    out_string = apply_filter(
        in_json, format_label_elements.main, "latex", in_format="json")

    assert out_string.strip() == "\n".join([
        r"\begin{figure}[]",
        r"\hypertarget{label1}{%",
        r"\begin{center}",
        r"\adjustimage{max size={0.9\linewidth}{0.9\paperheight},}"
        r"{path/to/image.png}",
        r"\end{center}",
        r"\caption{a title}\label{label1}",
        "}",
        r"\end{figure}"
    ])


def test_table_html():
    """
    Some text

    a b
    - -
    1 2
    4 5

    Table: Caption. {#tbl:id}
    """
    in_json = (
        {
            "pandoc-api-version": [1, 17, 5, 1],
            "meta": {
                "$$references": {"t": "MetaMap", "c": {
                    "tbl:id": {"t": "MetaMap", "c": {
                        "type": {"t": "MetaString", "c": "Table"},
                        "number": {"t": "MetaString", "c": "1"}}}}}},
            "blocks": [{"t": "Para", "c": [
                {"t": "Str", "c": "Some"},
                {"t": "Space"},
                {"t": "Str", "c": "text"}]},
                {"t": "Div", "c": [
                    ["tbl:id", ["labelled-Table"], []],
                    [{"t": "Table", "c": [
                        [{"t": "Str", "c": "Caption."},
                         {"t": "Space"}],
                        [{"t": "AlignDefault"},
                         {"t": "AlignDefault"}],
                        [0, 0],
                        [[{"t": "Plain", "c": [{"t": "Str", "c": "a"}]}],
                         [{"t": "Plain", "c": [{"t": "Str", "c": "b"}]}]],
                        [[[{"t": "Plain", "c": [{"t": "Str", "c": "1"}]}],
                          [{"t": "Plain", "c": [{"t": "Str", "c": "2"}]}]],
                            [[{"t": "Plain", "c": [{"t": "Str", "c": "4"}]}],
                             [{"t": "Plain", "c": [{"t": "Str", "c": "5"}]}]
                             ]]]}]]}]}
    )
    out_string = apply_filter(
        in_json, format_label_elements.main, "html", in_format="json")

    assert out_string.strip() == "\n".join([
        '<p>Some text</p>',
        '<a id="tbl:id" class="anchor-link" name="#tbl:id">',
        '<table>',
        '<caption>Caption. </caption>',
        '<thead>',
        '<tr class="header">',
        '<th>a</th>',
        '<th>b</th>',
        '</tr>',
        '</thead>',
        '<tbody>',
        '<tr class="odd">',
        '<td>1</td>',
        '<td>2</td>',
        '</tr>',
        '<tr class="even">',
        '<td>4</td>',
        '<td>5</td>',
        '</tr>',
        '</tbody>',
        '</table>',
        '</a>'])


def test_table_rst():
    """
    Some text

    a b
    - -
    1 2
    4 5

    Table: Caption. {#tbl:id}
    """
    in_json = (
        {
            "pandoc-api-version": [1, 17, 5, 1],
            "meta": {
                "$$references": {"t": "MetaMap", "c": {
                    "tbl:id": {"t": "MetaMap", "c": {
                        "type": {"t": "MetaString", "c": "Table"},
                        "number": {"t": "MetaString", "c": "1"}}}}}},
            "blocks": [{"t": "Para", "c": [
                {"t": "Str", "c": "Some"},
                {"t": "Space"},
                {"t": "Str", "c": "text"}]},
                {"t": "Div", "c": [
                    ["tbl:id", ["labelled-Table"], []],
                    [{"t": "Table", "c": [
                        [{"t": "Str", "c": "Caption."},
                         {"t": "Space"}],
                        [{"t": "AlignDefault"},
                         {"t": "AlignDefault"}],
                        [0, 0],
                        [[{"t": "Plain", "c": [{"t": "Str", "c": "a"}]}],
                         [{"t": "Plain", "c": [{"t": "Str", "c": "b"}]}]],
                        [[[{"t": "Plain", "c": [{"t": "Str", "c": "1"}]}],
                          [{"t": "Plain", "c": [{"t": "Str", "c": "2"}]}]],
                            [[{"t": "Plain", "c": [{"t": "Str", "c": "4"}]}],
                             [{"t": "Plain", "c": [{"t": "Str", "c": "5"}]}]
                             ]]]}]]}]}
    )
    out_string = apply_filter(
        in_json, format_label_elements.main, "rst", in_format="json")

    assert out_string.strip().splitlines()[0:3] == [
        'Some text', '', '.. _`tbl:id`:'
        ]
