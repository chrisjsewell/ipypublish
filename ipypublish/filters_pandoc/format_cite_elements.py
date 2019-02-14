""" a panflute filter to format Cite elements

The :py:mod:`ipypublish.filters_pandoc.prepare_cites` filter should be run
first to access the functionality below:

"""
from panflute import Element, Doc, Span, Cite  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import ATTRIBUTE_CITE_CLASS
from ipypublish.filters_pandoc.prepare_raw import CONVERTED_CITE_CLASS

from ipypublish.filters_pandoc.definitions import (
    PREFIX_MAP_LATEX, PREFIX_MAP_RST, IPUB_META_ROUTE
)


def format_cites(cite, doc):
    # type: (Cite, Doc) -> Element
    """
    originally adapted from:
    `pandoc-xnos <https://github.com/tomduck/pandoc-xnos/>`_
    """
    if not isinstance(cite, pf.Cite):
        return None

    # default tags for latex and rst
    cite_tag = doc.get_metadata(IPUB_META_ROUTE + ".reftag", "cref")
    cite_role = "cite"

    # check is the Cite has a surrounding Span to supply attributed
    span = None
    if (isinstance(cite.parent, pf.Span)
            and ATTRIBUTE_CITE_CLASS in cite.parent.classes):
        span = cite.parent

        if "prefix" in span.attributes:
            cite_tag = dict(PREFIX_MAP_LATEX).get(
                span.attributes["prefix"], cite_tag)
            cite_role = dict(PREFIX_MAP_RST).get(
                span.attributes["prefix"], cite_role)

    if (cite_role == "numref" and
            (not doc.get_metadata(IPUB_META_ROUTE + ".use_numref", False))):
        cite_role = "ref"

    if doc.format in ("latex", "tex"):

        if cite_tag in ['cite', 'cref', 'Cref'] or len(cite.citations) == 1:
            # multiple labels are allowed
            return pf.RawInline("\\{0}{{{1}}}".format(
                cite_tag,
                ",".join([c.id for c in cite.citations])), format="tex")
        else:
            tex = (
                ", ".join(['\\{0}{{{1}}}'.format(cite_tag, c.id)
                           for c in cite.citations[:-1]]) +
                ' and \\{0}{{{1}}}'.format(cite_tag, cite.citations[-1].id))
            return pf.RawInline(tex, format='tex')

    if doc.format == "rst":
        if len(cite.citations) == 1:
            raw = pf.RawInline(
                ":{0}:`{1}`".format(cite_role, cite.citations[0].id),
                format='rst')
        else:
            raw = pf.RawInline(
                ", ".join([':{0}:`{1}`'.format(cite_role, c.id)
                          for c in cite.citations[:-1]]) +
                ' and :{0}:`{1}`'.format(cite_role, cite.citations[-1].id),
                format="rst")

        # in testing, rst cite roles required space either side
        # to render correctly
        # TODO check if spacing is required for :cite: roles (and others)
        if cite_role == "cite":
            elem = span if span else cite  # type: pf.Inline
            raw = [raw]
            if elem.prev and not isinstance(elem.prev, pf.Space):
                raw.insert(0, pf.Space())
            if elem.next and not isinstance(elem.next, pf.Space):
                raw.append(pf.Space())

        return raw


def format_span_cites(span, doc):
    # type: (Cite, Doc) -> Element
    if not isinstance(span, pf.Span):
        return None

    if CONVERTED_CITE_CLASS not in span.classes:
        return None

    if doc.format in ("latex", "tex"):
        cite_tag = "cite"
        if span.attributes["format"] == "latex":
            cite_tag = span.attributes["tag"]
        # TODO use cref for rst ref/numref
        return pf.RawInline("\\{0}{{{1}}}".format(
            cite_tag, span.identifier, format="tex"))

    if doc.format == "rst":
        cite_role = "cite"
        if span.attributes["format"] == "rst":
            cite_role = span.attributes["role"]
        # TODO use ref for latex ref/cref/Cref
        return [
            pf.RawInline(
                ":{0}:`{1}`".format(cite_role, span.identifier),
                format='rst')
        ]

    if doc.format in ("html", "html5"):
        # <cite data-cite="cite_key">text</cite>
        return ([pf.RawInline(
                '<cite data-cite="{}">'.format(span.identifier),
                format="html")] +
                list(span.content) +
                [pf.RawInline('</cite>', format="html")])


def prepare(doc):
    # type: (Doc) -> None
    pass


def finalize(doc):
    # type: (Doc) -> None
    pass


def strip_cite_spans(span, doc):
    # type: (Span, Doc) -> Element
    if isinstance(span, pf.Span) and ATTRIBUTE_CITE_CLASS in span.classes:
        return list(span.content)


def main(doc=None, strip_spans=True):
    # type: (Doc) -> None
    to_run = [format_cites]
    if strip_spans:
        to_run.append(strip_cite_spans)
    return pf.run_filters(to_run,
                          prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
