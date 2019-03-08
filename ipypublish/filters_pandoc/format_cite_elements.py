""" a panflute filter to format Cite elements

The :py:mod:`ipypublish.filters_pandoc.prepare_cites` filter should be run
first to access the functionality below:

"""
from panflute import Element, Doc, Span, Cite  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import (
    ATTRIBUTE_CITE_CLASS, CONVERTED_CITE_CLASS,
    IPUB_META_ROUTE, CITE_HTML_NAMES
)
from ipypublish.filters_pandoc.html_bib import (
    read_bibliography, process_bib_entry
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
    cite_tag = doc.get_metadata(IPUB_META_ROUTE + ".reftag", "cite")
    cite_role = "cite"
    html_capitalize = False

    # check is the Cite has a surrounding Span to supply attributed
    span = None
    if (isinstance(cite.parent, pf.Span)
            and ATTRIBUTE_CITE_CLASS in cite.parent.classes):
        span = cite.parent

        cite_tag = span.attributes.get("latex", cite_tag)
        cite_role = span.attributes.get("rst", cite_role)
        html_capitalize = "capital" in span.classes

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
        elif cite_role == "cite":
            raw = pf.RawInline(
                ":{0}:`{1}`".format(cite_role, ",".join(
                    [c.id for c in cite.citations])),
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

    if doc.format in ("html", "html5"):

        elements = []
        cites = set()
        names = dict()
        unknown = set()

        for citation in cite.citations:
            ref = doc.get_metadata(
                "$$references.{}".format(citation.id), False)
            if ref:
                # ref -> e.g. {"type": "Math", "number": 1}
                prefix = dict(CITE_HTML_NAMES).get(ref["type"], ref["type"])
                prefix = prefix.capitalize() if html_capitalize else prefix

                # label = "{} {}".format(prefix, ref["number"])
                # elements.append(pf.RawInline(
                #     '<a href="#{0}">{1}</a>'.format(citation.id, label),
                #     format=doc.format))
                # found_ref = True

                names.setdefault(prefix, set()).add(
                    '<a href="#{0}">{1}</a>'.format(citation.id, ref["number"])
                )

            elif citation.id in doc.bibdatabase:
                cites.add(process_bib_entry(
                        citation.id, doc.bibdatabase, doc.bibnums))
                # elements.append(pf.RawInline(
                #     process_bib_entry(
                #         citation.id, doc.bibdatabase, doc.bibnums),
                #     format=doc.format))
                # found_ref = True
            else:
                unknown.add(citation.id)
                # elements.append(pf.Cite(citations=[citation]))

        # if found_ref:
        #     return elements
        # else:
            # return pf.RawInline(
            #     '<span style="background-color:rgba(225, 0, 0, .5)">'
            #     # 'No reference found for: {}</span>'.format(
            #     '{}</span>'.format(
            #         ", ".join([c.id for c in cite.citations])))

        elements = []
        if cites:
            # TODO sort
            elements.append(pf.RawInline(
                '<span>[{}]</span>'.format(",".join(c for c in cites)),
                format=doc.format))
        if names:
            # TODO sort
            for prefix, labels in names.items():
                elements.append(pf.RawInline(
                    '<span>{} {}</span>'.format(
                        prefix, ",".join(l for l in labels)),
                    format=doc.format))
        if unknown:
            elements.append(pf.RawInline(
                '<span style="background-color:rgba(225, 0, 0, .5)">'
                # 'No reference found for: {}</span>'.format(
                '{}</span>'.format(
                    ", ".join([l for l in unknown]))))

        return elements


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
    doc.bibnums = {}
    doc.bibdatabase = {}
    if doc.format in ("html", "html5"):
        bib_path = doc.get_metadata("ipub.bibliography", None)
        if bib_path:
            doc.bibdatabase = read_bibliography(bib_path)


def finalize(doc):
    # type: (Doc) -> None
    del doc.bibnums
    del doc.bibdatabase


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
