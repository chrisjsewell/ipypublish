""" a panflute filter to format Span element
representations of RawInline elements

The :py:mod:`ipypublish.filters_pandoc.prepare_raw` filter should be run
first to access the functionality below:

"""
from panflute import Element, Doc, Span  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import (
    CONVERTED_OTHER_CLASS, CONVERTED_CITE_CLASS,
    RAWSPAN_CLASS, RAWDIV_CLASS, CONVERTED_CITE_CLASS, CONVERTED_OTHER_CLASS
)


def process_raw_spans(container, doc):
    # type: (Span, Doc) -> Element
    if not isinstance(container, (pf.Span, pf.Div)):
        return None
    if CONVERTED_OTHER_CLASS not in container.classes:
        return None

    if isinstance(container, pf.Span):
        if doc.format == "rst" and container.attributes["format"] == "latex":
            if container.attributes["tag"] in ["todo"]:
                return pf.Str("\n\n.. {}:: {}\n\n".format(
                    container.attributes["tag"], container.attributes["content"]))

        return pf.RawInline(container.attributes.get("original"),
                            format=container.attributes["format"])
    else:
        if doc.format in ("rst", "html", "html5"):
            # we need to indent each paragraph of the directive
            content = [container.content[0]]
            for para in container.content[1:]:
                para.content = [pf.Str("    ")] + list(para.content)
                content.append(para)

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
                return pf.RawBlock(pf.stringify(pf.Div(*content)),
                                   format=container.attributes["format"])

            # TODO latex conversion


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
