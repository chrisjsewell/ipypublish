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
        if doc.format in ("rst", "html", "html5"):

            # convert the directive head, which will be e.g.
            # Para(Str(..) Space Str(toctree::) SoftBreak Str(:maxdepth:) Space Str(2) SoftBreak Str(:numbered:))  # noqa
            # we need to spilt on the soft breaks,
            # place them on a new line and indent

            # head = list(container.content[0].content)
            # split_head = [
            #     list(y) for x, y in itertools.groupby(
            #         head, lambda z: isinstance(z, pf.SoftBreak)) if not x]
            # if len(split_head) == 1:
            #     content.append(pf.Para(*split_head[0]))
            # else:
            #     content.append(pf.Plain(*split_head[0]))
            #     content.append(pf.RawBlock("\n", "rst"))
            #     for option in split_head[1:]:
            #         content.append(pf.Plain(*([pf.Space()] * 4 + option)))
            #         content.append(pf.RawBlock("\n", "rst"))
            #     content.append(pf.RawBlock("\n", "rst"))

            content = split_soft_breaks(container.content[0],
                                        indent_first=False)

            for para in container.content[1:]:
                # we need to indent each paragraph of the directive
                # para.content = [pf.Space()]*4 + list(para.content)
                content.extend(split_soft_breaks(
                    para, indent_first=True))

            if (doc.format in ("html", "html5")
                    and container.attributes["format"] == "rst"):
                return pf.RawBlock(
                    '<div {0} style="background-color:rgba(10, 225, 10, .2)">'
                    '{1}</div>'.format(
                        container.attributes.get("directive", ""),
                        "".join([
                            "<p>"+pf.stringify(c)+"</p>" for c in content])),
                    format="html"
                )
            else:
                return pf.RawBlock(pf.stringify(pf.Doc(*content)),
                                   format=container.attributes["format"])

    if (CONVERTED_OTHER_CLASS in container.classes
            and isinstance(container, pf.Div)):
        return pf.RawBlock(pf.stringify(
            pf.Doc(*container.content)),
            format=container.attributes["format"])

    # TODO latex conversion


def split_soft_breaks(container, delim="\n",
                      indent=4, fmt="rst", indent_first=False):
    """rst conversion doesn't recognise soft breaks as new lines,
    so add them manually and return a list containing the new elements
    """
    content = []

    chunks = [list(y) for x, y in itertools.groupby(
        container.content,
        lambda z: isinstance(z, pf.SoftBreak)) if not x]

    for i, chunk in enumerate(chunks):
        if i > 0 or indent_first:
            chunk = [pf.Space()] * indent + chunk
        content.append(pf.Plain(*chunk))
        content.append(pf.RawBlock("\n", fmt))

    if isinstance(container, pf.Para):
        content.append(pf.RawBlock("\n", fmt))

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
