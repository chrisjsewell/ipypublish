""" a panflute filter to format Span element
representations of RawInline elements

The :py:mod:`ipypublish.filters_pandoc.prepare_raw` filter should be run
first to access the functionality below:

"""
import itertools
# from textwrap import fill as textwrap

from panflute import Element, Doc, Span  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import (
    CONVERTED_OTHER_CLASS, CONVERTED_DIRECTIVE_CLASS, IPUB_META_ROUTE
)


def process_raw_spans(container, doc):
    # type: (Span, Doc) -> Element
    if not isinstance(container, (pf.Span, pf.Div)):
        return None

    hide_raw = doc.get_metadata(IPUB_META_ROUTE + ".hide_raw", False)

    if (CONVERTED_OTHER_CLASS in container.classes
            and isinstance(container, pf.Span)):
        if doc.format == "rst" and container.attributes["format"] == "latex":
            if container.attributes["tag"] in ["todo"]:
                return pf.Str("\n\n.. {}:: {}\n\n".format(
                    container.attributes["tag"],
                    container.attributes["content"]))
            if container.attributes["tag"] == "ensuremath":
                return pf.RawInline(":math:`{}`".format(
                    container.attributes["content"]), format='rst')

        return pf.RawInline(container.attributes.get("original"),
                            format=container.attributes["format"])

    if (CONVERTED_DIRECTIVE_CLASS in container.classes
            and isinstance(container, pf.Div)):
        # convert the directive head, which will be e.g.
        # Para(Str(..) Space Str(toctree::) SoftBreak Str(:maxdepth:) Space Str(2) SoftBreak Str(:numbered:))  # noqa
        # we need to spilt on the soft breaks,
        # place them on a new line and re-indent them

        if doc.format in ("rst"):

            # split into lines by soft breaks
            header_lines = [list(y) for x, y in itertools.groupby(
                container.content[0].content,
                lambda z: isinstance(z, pf.SoftBreak)) if not x]

            # wrap each line in a Para and convert block with pandoc
            head_doc = pf.Doc(*[pf.Para(*l) for l in header_lines])
            head_doc.api_version = doc.api_version
            head_str = pf.convert_text(head_doc,
                                       input_format="panflute",
                                       output_format=doc.format)
            # remove blank lines and indent
            head_str = head_str.replace("\n\n", "\n    ") + "\n\n"
            head_block = pf.RawBlock(head_str, format=doc.format)

            if len(container.content) == 1:
                return head_block

            # split into lines by soft breaks, we use indicators to tell
            # us where to indent in the converted text
            body_blocks = []
            for block in container.content[1:]:
                new_elements = [pf.RawInline("%^*", format=doc.format)]
                for el in block.content:
                    if isinstance(el, pf.SoftBreak):
                        new_elements.append(
                            pf.RawInline("?&@", format=doc.format))
                    else:
                        new_elements.append(el)
                block.content = new_elements
                body_blocks.append(block)

            # convert body content with pandoc
            body_doc = pf.Doc(*body_blocks)
            body_doc.api_version = doc.api_version
            body_str = pf.convert_text(body_doc,
                                       input_format="panflute",
                                       output_format=doc.format)
            # raise ValueError(body_blocks)
            body_str = body_str.replace(
                "%^*", "    ").replace("?&@", "\n    ")

            # ensure all lines are indented correctly
            # (doesn't occur by default?)
            body_str = "\n".join(
                ["    " + l.lstrip() if l.strip() else l
                 for l in body_str.splitlines()]) + '\n\n'

            body_block = pf.RawBlock(body_str, format=doc.format)
            return [head_block, body_block]

        elif (doc.format in ("html", "html5")
                and container.attributes["format"] == "rst"):

            if hide_raw:
                return []

            head_para = pf.Para(
                *[pf.RawInline("<br>" + "&nbsp" * 4)
                  if isinstance(c, pf.SoftBreak)
                  else c
                  for c in container.content[0].content])
            head_str = pf.convert_text(head_para,
                                       input_format="panflute",
                                       output_format=doc.format)

            if len(container.content) > 1:

                body_doc = pf.Doc(*container.content[1:])
                body_doc.api_version = doc.api_version
                body_str = pf.convert_text(body_doc,
                                           input_format="panflute",
                                           output_format=doc.format)
                body_str = ('<p></p><div style="margin-left: 20px">'
                            '{0}</div>').format(body_str)
            else:
                body_str = ""

            return pf.RawBlock(
                '<div {0} style="background-color:rgba(10, 225, 10, .2)">'
                '{1}{2}'
                '</div>'.format(
                    container.attributes.get("directive", ""),
                    head_str,
                    body_str
                ),
                format="html"
            )

        elif (doc.format in ("tex", "latex")
                and container.attributes["format"] == "rst"):

            if hide_raw:
                return []

            directive = container.attributes.get("directive", "")
            inline = container.attributes.get("inline", "")
            # TODO handle directive with options and/or inline body
            # e.g. .. figure:: path/to/figure
            #          :centre:

            box_open = (
                "\\begin{{mdframed}}"
                "[frametitle={{{0}}},frametitlerule=true]".format(directive)
            )
            if inline:
                box_open += "\n\\mdfsubtitle{{{0}}}".format(inline)
            box_close = "\\end{mdframed}"

            if len(container.content) == 1:
                return pf.RawBlock(
                    box_open + box_close,
                    format="tex")
            else:
                return (
                    [pf.RawBlock(box_open, format="tex")] +
                    list(container.content[1:]) +
                    [pf.RawBlock(box_close, format="tex")]
                )

        return pf.RawBlock(pf.stringify(pf.Doc(*container.content)),
                           format=container.attributes["format"])

    if (CONVERTED_OTHER_CLASS in container.classes
            and isinstance(container, pf.Div)):
        return pf.RawBlock(pf.stringify(
            pf.Doc(*container.content)),
            format=container.attributes["format"])


# now unused
# def split_soft_breaks(container,
#                       indent=4, fmt="rst", indent_first=False,
#                       pre_content="", post_content="",
#                       pre_chunk="", post_chunk="",
#                       linebreak="\n", raw_indent=None):
#     """rst conversion doesn't recognise soft breaks as new lines,
#     so add them manually and return a list containing the new elements
#     """
#     content = []
#     if pre_content:
#         content.append(pf.RawBlock(pre_content, fmt))

#     chunks = [list(y) for x, y in itertools.groupby(
#         container.content,
#         lambda z: isinstance(z, pf.SoftBreak)) if not x]

#     for i, chunk in enumerate(chunks):
#         if i > 0 or indent_first:
#             if raw_indent is not None:
#                 chunk = [pf.RawInline(raw_indent, fmt)] * indent + chunk
#             else:
#                 chunk = [pf.Space()] * indent + chunk

#         if pre_chunk:
#             content.append(pf.RawBlock(pre_chunk, fmt))
#         content.append(pf.Plain(*chunk))
#         content.append(pf.RawBlock(linebreak, fmt))
#         if post_chunk:
#             content.append(pf.RawBlock(post_chunk, fmt))

#     # if isinstance(container, pf.Para):
#     #     content.append(pf.RawBlock(linebreak, fmt))

#     if post_content:
#         content.append(pf.RawBlock(post_content, fmt))

#     return content

def process_code_latex(code, doc):
    # type: (pf.CodeBlock, Doc) -> Element
    if doc.format not in ("tex", "latex"):
        return None
    if not isinstance(code, pf.CodeBlock):
        return None
    # TODO line wrapping
    return [
        pf.RawBlock("\\begin{mdframed}", format=doc.format),
        code,
        pf.RawBlock("\\end{mdframed}", format=doc.format),
    ]


def prepare(doc):
    # type: (Doc) -> None
    pass


def finalize(doc):
    # type: (Doc) -> None
    pass


def main(doc=None):
    # type: (Doc) -> None
    """
    """
    return pf.run_filters([process_raw_spans, process_code_latex],
                          prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
