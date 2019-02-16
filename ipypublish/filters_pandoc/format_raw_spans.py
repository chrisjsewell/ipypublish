""" a panflute filter to format Span element
representations of RawInline elements

The :py:mod:`ipypublish.filters_pandoc.prepare_raw` filter should be run
first to access the functionality below:

"""
import itertools

from panflute import Element, Doc, Span  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import (
    CONVERTED_OTHER_CLASS, CONVERTED_DIRECTIVE_CLASS
)


def process_raw_spans(container, doc):
    # type: (Span, Doc) -> Element
    if not isinstance(container, (pf.Span, pf.Div)):
        return None

    if (CONVERTED_OTHER_CLASS in container.classes
            and isinstance(container, pf.Span)):
        if doc.format == "rst" and container.attributes["format"] == "latex":
            if container.attributes["tag"] in ["todo"]:
                return pf.Str("\n\n.. {}:: {}\n\n".format(
                    container.attributes["tag"], container.attributes["content"]))

        return pf.RawInline(container.attributes.get("original"),
                            format=container.attributes["format"])

    if (CONVERTED_DIRECTIVE_CLASS in container.classes
            and isinstance(container, pf.Div)):
        # convert the directive head, which will be e.g.
        # Para(Str(..) Space Str(toctree::) SoftBreak Str(:maxdepth:) Space Str(2) SoftBreak Str(:numbered:))  # noqa
        # we need to spilt on the soft breaks,
        # place them on a new line and re-indent them
        if doc.format in ("rst"):

            content = split_soft_breaks(container.content[0],
                                        indent_first=False, indent=4)
            for para in container.content[1:]:
                content.extend(split_soft_breaks(
                    para, indent_first=True, indent=4))

            return pf.RawBlock(pf.stringify(pf.Doc(*content)),
                               format="rst")

        elif (doc.format in ("html", "html5")
                and container.attributes["format"] == "rst"):
            # TODO option to show or hide rst directives in html output
            content = split_soft_breaks(
                container.content[0], indent_first=False, indent=4, fmt="html",
                pre_content="<p>", post_content="</p>", post_chunk="<br>",
                raw_space="&nbsp")
            for para in container.content[1:]:
                content.extend(split_soft_breaks(
                    para, indent_first=True, indent=4, fmt="html",
                    pre_content='<p>', post_content="</p>", post_chunk="<br>",
                    raw_space="&nbsp"))

            return pf.RawBlock(
                '<div {0} style="background-color:rgba(10, 225, 10, .2)">'
                '{1}</div>'.format(
                    container.attributes.get("directive", ""),
                    pf.stringify(pf.Doc(*content))
                ),
                format="html"
            )

    if (CONVERTED_OTHER_CLASS in container.classes
            and isinstance(container, pf.Div)):
        return pf.RawBlock(pf.stringify(
            pf.Doc(*container.content)),
            format=container.attributes["format"])

    # TODO latex conversion


def split_soft_breaks(container,
                      indent=4, fmt="rst", indent_first=False,
                      pre_content="", post_content="",
                      pre_chunk="", post_chunk="",
                      linebreak="\n", raw_space=None):
    """rst conversion doesn't recognise soft breaks as new lines,
    so add them manually and return a list containing the new elements
    """
    content = []
    if pre_content:
        content.append(pf.RawBlock(pre_content, fmt))

    chunks = [list(y) for x, y in itertools.groupby(
        container.content,
        lambda z: isinstance(z, pf.SoftBreak)) if not x]

    for i, chunk in enumerate(chunks):
        if i > 0 or indent_first:
            if raw_space is not None:
                chunk = [pf.RawInline(raw_space, fmt)] * indent + chunk
            else:
                chunk = [pf.Space()] * indent + chunk

        if pre_chunk:
            content.append(pf.RawBlock(pre_chunk, fmt))
        content.append(pf.Plain(*chunk))
        content.append(pf.RawBlock(linebreak, fmt))
        if post_chunk:
            content.append(pf.RawBlock(post_chunk, fmt))

    if isinstance(container, pf.Para):
        content.append(pf.RawBlock(linebreak, fmt))

    if post_content:
        content.append(pf.RawBlock(post_content, fmt))

    return content


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
    return pf.run_filter(process_raw_spans,
                         prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
