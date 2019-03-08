"""pandoc filters used in converting markdown to a target format

Other sources of information:

- [Pandoc User Guide](https://pandoc.org/MANUAL.html#citations)
- [List of Pandoc Elements](https://metacpan.org/pod/Pandoc::Elements)
- [reStructuredText Primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [reStructuredText Directives](http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure)
- [sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html)

"""  # noqa: E501
import panflute as pf

from ipypublish.filters_pandoc.definitions import IPUB_META_ROUTE
from ipypublish.filters_pandoc.utils import (
    apply_filter, get_option, create_ipub_meta)
from ipypublish.filters_pandoc import (
    prepare_cites, prepare_labels, prepare_raw,
    format_cite_elements, format_label_elements, format_raw_spans,
    rmarkdown_to_mpe
)


def pandoc_filters():
    """ run a set of ipypublish pandoc filters directly on the pandoc AST,
    via ``pandoc --filter ipubpandoc``
    """
    doc = pf.load()

    # in an rmarkdown file, the metadata will be under a root `jupyter` key
    jmeta = doc.get_metadata('jupyter', {})
    meta = pf.tools.meta2builtin(doc.metadata)
    if 'jupyter' in meta and hasattr(meta["jupyter"], 'items'):
        jmeta = meta.pop("jupyter")
        meta.update(jmeta)
        doc.metadata = meta  # builtin2meta(meta)

    apply_filters = doc.get_metadata(IPUB_META_ROUTE + ".apply_filters",
                                     default=True)
    convert_raw = doc.get_metadata(IPUB_META_ROUTE + ".convert_raw",
                                   default=True)

    if apply_filters:
        if convert_raw:
            filters = [
                prepare_raw.main,
                prepare_cites.main,
                prepare_labels.main,
                format_cite_elements.main,
                format_raw_spans.main,
                format_label_elements.main,
                rmarkdown_to_mpe.main
            ]
        else:
            filters = [
                prepare_cites.main,
                prepare_labels.main,
                format_cite_elements.main,
                format_label_elements.main,
                rmarkdown_to_mpe.main
            ]
    else:
        filters = []

    out_doc = doc
    for func in filters:
        out_doc = func(out_doc)  # type: pf.Doc
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

    **Available Meta Options**

    The following options are available in {"ipub": {}}

    apply_filters=True: bool
        apply filters to markdown
    convert_raw=True: bool
        if True attempt to extract non-markdown formats
        and convert them to the target format, e.g. rst roles to latex tags
    at_notation=True: bool
        interpret @label as a reference type based on its prefix modifier,
        latex: '' = cite '+' = cref,    '^' = Cref,    '!' = ref,  '=' = eqref
        rst: '' = :cite: '+' = :numref: '^' = :numref: '!' = :ref: '=' = :eq:
    reftag="cite": str
        default latex tag for references
    use_numref=True: bool
        whether to use the ``:numref:`` role or just ``:ref:``
        ``:numref:`` requires ``numfig = True`` in conf.py and,
        for section numbering, a toc tree with ``:numbered:``
    strip_meta=True: bool
        if True strip any source metadata, contained in the top matter

    The options will be taken in order of preference from:
    source.metadata > cell.metadata > nb.metadata

    For source.metadata, see https://pandoc.org/MANUAL.html#metadata-blocks:

    .. code-block:: yaml

        ---
        ipub:
          pandoc:
            use_numref: True
        ---
        +@label

    """
    if not source.strip():
        return source.strip() if strip else source

    # convert the source to a format agnostic Doc
    doc = apply_filter(source, dry_run=True)  # type: pf.Doc

    # find the preferential versions of the metadata values
    # TODO a make this autopopulate (possibly from schema)
    option_preference = [doc.metadata, cell_metadata, nb_metadata]
    apply_filters = get_option(option_preference,
                               keypath=IPUB_META_ROUTE + ".apply_filters",
                               default=True)
    convert_raw = get_option(option_preference,
                             keypath=IPUB_META_ROUTE + ".convert_raw",
                             default=True)
    hide_raw = get_option(option_preference,
                          keypath=IPUB_META_ROUTE + ".hide_raw",
                          default=False)
    numref = get_option(option_preference,
                        keypath=IPUB_META_ROUTE + ".use_numref", default=True)
    at_notation = get_option(option_preference,
                             keypath=IPUB_META_ROUTE + ".at_notation",
                             default=True)
    reftag = get_option(option_preference,
                        keypath=IPUB_META_ROUTE + ".reftag", default="cite")
    strip_meta = get_option(option_preference,
                            keypath=IPUB_META_ROUTE + ".strip_meta",
                            default=True)

    if apply_filters:
        # TODO store the original metadata and replace it at end?
        # original_meta = copy.deepcopy(doc.metadata)

        # set metadata with preferential values
        meta = pf.tools.meta2builtin(doc.metadata)
        meta.update(create_ipub_meta({
            "use_numref": numref,
            "at_notation": at_notation,
            "reftag": reftag,
            "hide_raw": hide_raw
        }))
        doc.metadata = meta  # builtin2meta(meta)

        # doc.metadata["ipub"]["use_numref"] = builtin2meta(numref)
        # doc.metadata["ipub"]["at_notation"] = builtin2meta(at_notation)
        # doc.metadata["ipub"]["reftag"] = builtin2meta(reftag)

        # set filters
        if convert_raw:
            filters = [
                prepare_raw.main,
                prepare_cites.main,
                prepare_labels.main,
                format_cite_elements.main,
                format_raw_spans.main,
                format_label_elements.main
            ]
        else:
            filters = [
                prepare_cites.main,
                prepare_labels.main,
                format_cite_elements.main,
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
