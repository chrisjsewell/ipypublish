""" a panflute filter to format Span element
representations of RawInline elements

The :py:mod:`ipypublish.filters_pandoc.prepare_raw` filter should be run
first to access the functionality below:

"""
from panflute import Element, Doc, Span  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.prepare_raw import (
    CONVERTED_OTHER_CLASS, CONVERTED_CITE_CLASS)


def process_raw_spans(span, doc):
    # type: (Span, Doc) -> Element
    if not isinstance(span, pf.Span):
        return None
    if CONVERTED_OTHER_CLASS not in span.classes:
        return None

    if doc.format == "rst" and span.attributes["format"] == "latex":
        if span.attributes["tag"] in ["todo"]:
            return pf.Str("\n\n.. {}:: {}\n\n".format(
                span.attributes["tag"], span.attributes["content"]))

    return pf.RawInline(span.attributes.get("original"),
                        format=span.attributes["format"])


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
