import sys
import pytest
from ipypublish.filters_pandoc.utils import apply_filter
from ipypublish.filters_pandoc.prepare_cites import main


def test_para_rst():
    """
    """
    in_string = [
        "+@label{.class a=1} xyz *@label2* @label3{.b}",
        "",
        "(@label4{})",
        "",
        "(@label5{.b} x)"
    ]
    out_string = apply_filter(in_string, main, "rst")

    assert out_string.strip() == "\n".join([
        "@label xyz *@label2* @label3",
        "",
        "(@label4)",
        "",
        "(@label5 x)"
    ])


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="html attributes not in same order")
def test_para_html():
    """
    """
    in_string = [
        "+@label{ .class a=1} xyz *@label2* @label3{ .b}"
    ]
    out_string = apply_filter(in_string, main, "html")

    assert out_string.strip() == "\n".join([
        '<p>'
        '<span class="attribute-Cite class" '
        'data-latex="cref" data-rst="numref" data-a="1">'
        '<span class="citation" data-cites="label">@label</span>'
        '</span> '
        'xyz '
        '<em><span class="citation" data-cites="label2">@label2</span></em> '
        '<span class="attribute-Cite b">'
        '<span class="citation" data-cites="label3">@label3</span>'
        '</span>'
        '</p>',
    ])


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="html attributes not in same order")
def test_table_html():
    """
    """
    in_string = [
        "a b",
        "- -",
        "x y",
        "",
        "Table: Caption +@label"
    ]
    out_string = apply_filter(in_string, main, "html")

    assert out_string.strip() == "\n".join([
         '<table>',
         '<caption>Caption '
         '<span class="attribute-Cite" data-latex="cref" data-rst="numref">'
         '<span class="citation" data-cites="label">@label</span>'
         '</span></caption>',
         '<thead>',
         '<tr class="header">',
         '<th>a</th>',
         '<th>b</th>',
         '</tr>',
         '</thead>',
         '<tbody>',
         '<tr class="odd">',
         '<td>x</td>',
         '<td>y</td>',
         '</tr>',
         '</tbody>',
         '</table>'
    ])


@pytest.mark.skipif(sys.version_info < (3, 6),
                    reason="html attributes not in same order")
def test_image_html():

    in_string = [
        "![a title with a @label1 +@label2 {.nclass x=3}](path/to/image.png)"
    ]
    out_string = apply_filter(in_string, main, "html")

    assert out_string.strip() == "\n".join([
        '<figure>',
        '<img src="path/to/image.png" alt="a title with a @label1 @label2" />'
        '<figcaption>a title with a '
        '<span class="citation" data-cites="label1">@label1</span> '
        '<span class="attribute-Cite nclass" '
        'data-latex="cref" data-rst="numref" data-x="3">'
        '<span class="citation" data-cites="label2">@label2</span>'
        '</span></figcaption>',
        '</figure>'
        ])
