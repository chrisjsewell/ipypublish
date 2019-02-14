"""pandoc filters used in converting markdown to a target format

Other sources of information:

- [Pandoc User Guide](https://pandoc.org/MANUAL.html#citations)
- [List of Pandoc Elements](https://metacpan.org/pod/Pandoc::Elements)
- [reStructuredText Primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [reStructuredText Directives](http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure)
- [sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html)

"""
import panflute as pf
# from panflute.elements import builtin2meta
from ipypublish.filters_pandoc import builtin2meta

from ipypublish.filters_pandoc.utils import apply_filter, get_option
from ipypublish.filters_pandoc import (
    prepare_cites, prepare_labels, prepare_raw,
    format_cite_elements, format_label_elements, format_raw_spans
)


def pandoc_filters():
    """ run a set of ipypublish pandoc filters directly on the pandoc AST,
    via ``pandoc --filter ipubpandoc``
    """
    filters = [
        prepare_cites.main,
        prepare_labels.main,
        prepare_raw.main,
        format_cite_elements.main,
        format_raw_spans.main,
        format_label_elements.main
    ]

    doc = pf.load()
    out_doc = doc
    for func in filters:
        out_doc = func(out_doc)  # type: Doc
    # TODO strip meta?
    pf.dump(doc)


def jinja_filter(source, to_format, nb_metadata, cell_metadata,
                 from_format="markdown", strip=True):
    """run a set of ipypublish pandoc filters as a Jinja2 filter

    We convert the source to an intermediary pandoc-json AST format,
    run the pandocfilters, then convert to the to_format

    Parameters
    ----------
    source: str
        content to convert
    to_format: str
        format of output
    nb_metadata: dict
        mapping of notebook level metadata
    cell_metadata: dict
        mapping of cell level metadata
    from_format: str
        format of source
    strip: bool
        strip any blank lines from the start/end of the final string

    Notes
    -----

    if ``at_notation``, ``reftag``, ``use_numref`` are already set in the 
    source metadata, under key ``ipub``, this will preferentially be used.
    See https://pandoc.org/MANUAL.html#metadata-blocks, e.g.

    .. code-block:: yaml

        ---
        ipub:
            use_numref: True
        ---



    Available Meta Options
    ~~~~~~~~~~~~~~~~~~~~~~

    at_notation=True: bool
        interpret @label as a reference type based on its prefix modifier,
        latex: '' = cite '+' = cref,    '^' = Cref,    '!' = ref,  '=' = eqref
        rst: '' = :cite: '+' = :numref: '^' = :numref: '!' = :ref: '=' = :eq:
    reftag="cref": str
        default latex tag for references
    use_numref=True: bool
        whether to use the ``:numref:`` directive or just ``:ref:``
        ``:numref:`` requires ``numfig = True`` in conf.py and,
        for section numbering, a toc tree with ``:numbered:``
    strip_meta=True: bool
        if True strip any source metadata, contained in the top matter

    """
    if not source.strip():
        return source.strip() if strip else source

    # convert the source to a format agnostic Doc
    doc = apply_filter(source, dry_run=True)  # type: pf.Doc
    # store the original metadata
    # original_meta = copy.deepcopy(doc.metadata)

    # if the ipypublish options are not already in the metadata add them
    if "ipub" not in doc.metadata:
        doc.metadata["ipub"] = pf.MetaMap()
    filter_mkdown = get_option(doc.metadata, cell_metadata, nb_metadata,
                               keypath="ipub.filter_mkdown", default=True)
    numref = get_option(doc.metadata, cell_metadata, nb_metadata,
                        keypath="ipub.use_numref", default=True)
    at_notation = get_option(doc.metadata, cell_metadata, nb_metadata,
                             keypath="ipub.at_notation", default=True)
    reftag = get_option(doc.metadata, cell_metadata, nb_metadata,
                        keypath="ipub.reftag", default="cref")
    strip_meta = get_option(doc.metadata, cell_metadata, nb_metadata,
                            keypath="ipub.strip_meta", default=True)

    if filter_mkdown:
        doc.metadata["ipub"]["use_numref"] = builtin2meta(numref)
        doc.metadata["ipub"]["at_notation"] = builtin2meta(at_notation)
        doc.metadata["ipub"]["reftag"] = builtin2meta(reftag)
        filters = [
            prepare_cites.main,
            prepare_labels.main,
            prepare_raw.main,
            format_cite_elements.main,
            format_raw_spans.main,
            format_label_elements.main
        ]
    else:
        filters = []

    out_str = apply_filter(doc,
                           filters,
                           in_format=from_format,
                           out_format=to_format,
                           strip_meta=bool(strip_meta)
                           )
    if strip:
        out_str = out_str.strip()

    return out_str
