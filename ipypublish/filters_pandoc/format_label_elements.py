""" a panflute filter to format elements types
that may contain reference labels, i.e. Math, Image and Table.

The :py:mod:`ipypublish.filters_pandoc.prepare_labels` filter should be run
first to access the functionality below:

If the parent of the element is a Span (or Div for Table), with a class
labelled-Math/labelled-Image/labelled-Table,
then the label of the element will be span.identifier, and
the attributes and classes from this Span will be used to inform the format.

Additionally, for HTML, if a '$$references' key is available in the metadata,
this will be used to add a suffix to the element captions,
with the number of the element.

Finally, if main() is called with strip_spans = True (the default),
The Span/Div elements with classes labelled-Math/labelled-Image/labelled-Table
will be stripped from the document

"""
# TODO format headers with section labels
# (see ipysphinx.transforms.CreateNotebookSectionAnchors)
import json
from panflute import Element, Doc, Span, Div, Math, Image, Table  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.utils import convert_units, convert_attributes
from ipypublish.filters_pandoc.prepare_labels import (
    LABELLED_IMAGE_CLASS, LABELLED_MATH_CLASS, LABELLED_TABLE_CLASS
)

LATEX_FIG_LABELLED = """\\begin{{figure}}[{options}]
\\hypertarget{{{label}}}{{%
\\begin{{center}}
\\adjustimage{{max size={{0.9\\linewidth}}{{0.9\\paperheight}},{size}}}{{{path}}}
\\end{{center}}
\\caption{{{caption}}}\\label{{{label}}}
}}
\\end{{figure}}"""  # noqa: E501

LATEX_FIG_UNLABELLED = """\\begin{{figure}}[{options}]
\\begin{{center}}
\\adjustimage{{max size={{0.9\\linewidth}}{{0.9\\paperheight}},{size}}}{{{path}}}
\\end{{center}}
\\caption{{{caption}}}
\\end{{figure}}"""  # noqa: E501


def format_math(math, doc):
    # type: (Math, Doc) -> Element
    """
    originally adapted from:
    `pandoc-eqnos <https://github.com/tomduck/pandoc-eqnos/>`_
    """
    if not isinstance(math, pf.Math):
        return None

    if math.format != "DisplayMath":
        return None

    span = None
    number = ""
    env = "equation"
    label_tag = ""
    if (isinstance(math.parent, pf.Span)
            and LABELLED_MATH_CLASS in math.parent.classes):
        span = math.parent

        number = '*' if "unnumbered" in span.classes else ''
        env = span.attributes.get("env", "equation")
        if doc.format in ("tex", "latex"):
            label_tag = "\\label{{{0}}}".format(span.identifier)
        else:
            label_tag = ""

    # construct latex environment
    tex = '\\begin{{{0}{1}}}{2}{3}\\end{{{0}{1}}}'.format(
        env, number, math.text, label_tag)

    if doc.format in ("tex", "latex"):
        return pf.RawInline(tex, format="tex")

    elif doc.format in ("rst"):
        if not span:
            rst = '\n\n.. math::\n   :nowrap:\n\n   {0}\n\n'.format(tex)
        else:
            rst = (
                '\n\n.. math::\n   :nowrap:\n   :label: {0}'
                '\n\n   {1}\n\n'.format(span.identifier, tex))
        return pf.RawInline(rst, format="rst")

    elif doc.format in ('html', 'html5'):
        # new_span = pf.Span(anchor_start, math, anchor_end)
        # TODO add formatting
        # TODO name by count
        if span:
            math.text = tex
            return _wrap_in_anchor(math, span.identifier)
        else:
            return None


def format_image(image, doc):
    # type: (Image, Doc) -> Element
    """
    originally adapted from:
    `pandoc-fignos <https://github.com/tomduck/pandoc-fignos/>`_
    """
    if not isinstance(image, pf.Image):
        return None

    span = None
    if (isinstance(image.parent, pf.Span)
            and LABELLED_IMAGE_CLASS in image.parent.classes):
        span = image.parent

    if span is not None:
        identifier = span.identifier
        attributes = span.attributes
        #  classes = span.classes
    else:
        identifier = image.identifier
        attributes = image.attributes
        # classes = image.classes

    if doc.format in ("tex", "latex"):
        new_doc = Doc(pf.Para(*image.content))
        new_doc.api_version = doc.api_version
        if image.content:
            caption = pf.run_pandoc(json.dumps(new_doc.to_json()),
                                    args=["-f", "json", "-t", "latex"]).strip()
        else:
            caption = ""

        options = attributes.get("placement", "")
        size = ''  # max width set as 0.9\linewidth
        if "width" in attributes:
            width = convert_units(attributes['width'], "fraction")
            size = 'width={0}\\linewidth'.format(width)
        elif "height" in attributes:
            height = convert_units(attributes['height'], "fraction")
            size = 'height={0}\\paperheight'.format(height)

        if identifier:
            latex = LATEX_FIG_LABELLED.format(
                label=identifier,
                options=options,
                path=image.url,
                caption=caption,
                size=size)
        else:
            latex = LATEX_FIG_UNLABELLED.format(
                options=options,
                path=image.url,
                caption=caption,
                size=size)

        return pf.RawInline(latex, format="tex")

    elif doc.format in ("rst",):
        return image
        # TODO formatting and span identifier (convert width/height to %)

    elif doc.format in ("html", "html5"):
        if identifier:
            return _wrap_in_anchor(image, identifier)
        else:
            return image
        # TODO formatting, name by count
    else:
        return None


def format_table(table, doc):
    # type: (Table, Doc) -> Element
    """
    originally adapted from:
    `pandoc-tablenos <https://github.com/tomduck/pandoc-tablenos>`_
    """
    if not isinstance(table, pf.Table):
        return None

    div = None  # type: pf.Div
    if (isinstance(table.parent, pf.Div)
            and LABELLED_TABLE_CLASS in table.parent.classes):
        div = table.parent

    if div is None:
        return None

    attributes = convert_attributes(div.attributes)

    if "align" in div.attributes:
        align_text = attributes["align"]
        align = [
            {'l': 'AlignLeft',
             'r': 'AlignRight',
             'c': 'AlignCenter'}.get(a, None) for a in align_text]
        if None in align:
            raise ValueError(
                "table '{0}' alignment must contain only l,r,c:"
                " {1}".format(div.identifier, align_text))
        table.alignment = align
        attributes["align"] = align

    if "widths" in div.attributes:
        widths = attributes["widths"]
        try:
            widths = [float(w) for w in widths]
        except Exception:
            raise ValueError(
                "table '{0}' widths must be a list of numbers:"
                " {1}".format(div.identifier, widths))
        table.width = widths
        attributes["widths"] = widths

    if doc.format in ("tex", "latex"):
        # TODO placement
        table.caption.append(pf.RawInline(
            '\\label{{{0}}}'.format(div.identifier), format="tex"))
        return table

    if doc.format in ("rst",):
        # pandoc 2.6 doesn't output table options
        if attributes:
            tbl_doc = pf.Doc(table)
            tbl_doc.api_version = doc.api_version
            tbl_str = pf.convert_text(tbl_doc,
                                      input_format="panflute",
                                      output_format="rst")

            tbl_lines = tbl_str.splitlines()
            if tbl_lines[1].strip() == "":
                tbl_lines.insert(1, "   :align: center")
                if "widths" in attributes:
                    # in rst widths must be integers
                    widths = " ".join([str(int(w*10)) for w in table.width])
                    tbl_lines.insert(1, "   :widths: {}".format(widths))
            # TODO rst column alignment, see
            # https://cloud-sptheme.readthedocs.io/en/latest/lib/cloud_sptheme.ext.table_styling.html

            return [
                pf.Para(pf.RawInline(
                    '.. _`{0}`:'.format(div.identifier), format="rst")),
                pf.RawBlock("\n".join(tbl_lines)+"\n\n", format=doc.format)
            ]

        return [
            pf.Para(pf.RawInline(
                '.. _`{0}`:'.format(div.identifier), format="rst")),
            table
        ]

    if doc.format in ("html", "html5"):
        return _wrap_in_anchor(table, div.identifier, inline=False)
        # TODO formatting, name by count


def strip_labelled_spans(element, doc):
    # type: (Span, Doc) -> Element

    if isinstance(element, pf.Span) and set(element.classes).intersection([
        LABELLED_IMAGE_CLASS, LABELLED_MATH_CLASS
    ]):
        return list(element.content)

    if isinstance(element, pf.Div) and set(element.classes).intersection([
        LABELLED_TABLE_CLASS
    ]):
        return list(element.content)


def _wrap_in_anchor(element, label, inline=True):
    """ wrap element in html anchors

    according to https://stackoverflow.com/a/1828032/5033292
    can wrap inline and block elements in anchor in html5
    """
    if inline:
        raw = pf.RawInline
    else:
        raw = pf.RawBlock
    anchor_start = raw(
        '<a id="{0}" class="anchor-link" name="#{0}">'.format(
            label), format="html")
    anchor_end = raw("</a>", format="html")
    return [anchor_start, element, anchor_end]


def prepare(doc):
    # type: (Doc) -> None
    pass


def finalize(doc):
    # type: (Doc) -> None
    pass


def main(doc=None, strip_spans=True):
    # type: (Doc, bool) -> None
    to_run = [format_math, format_image, format_table]
    if strip_spans:
        to_run.append(strip_labelled_spans)
    return pf.run_filters(to_run,
                          prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
