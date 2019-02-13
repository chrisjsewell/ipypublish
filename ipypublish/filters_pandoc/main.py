"""pandoc filters used in converting markdown to a target format

Other sources of information:

- [Pandoc User Guide](https://pandoc.org/MANUAL.html#citations)
- [List of Pandoc Elements](https://metacpan.org/pod/Pandoc::Elements)
- [reStructuredText Primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [reStructuredText Directives](http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure)
- [sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html)

"""
import io

import panflute as pf

from ipypublish.filters_pandoc.utils import apply_filter
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
    pf.dump(doc)


def jinja_filter(source, to_format, from_format="markdown",
                 strip=True,
                 at_notation=True, reftag="cref", use_numref=True):
    """run a set of ipypublish pandoc filters as a Jinja2 filter

    We convert the source to an intermediary pandoc-json AST format,
    run the pandocfilters, then convert to the to_format

    Parameters
    ----------
    source: str
        content to convert
    from_format: str
        format of source
    to_format: str
        format of output
    strip: bool
        strip any blank lines from the start/end of the final string
    at_notation: bool
        interpret @label as a reference type based on its prefix modifier,
        latex: '' = cite '+' = cref,    '^' = Cref,    '!' = ref,  '=' = eqref
        rst: '' = :cite: '+' = :numref: '^' = :numref: '!' = :ref: '=' = :eq:
    reftag: str
        default latex tag for references
    use_numref: bool
        whether to use the ``:numref:`` directive or just ``:ref:``

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

    ``:numref:`` requires ``numfig = True`` in conf.py and,
    for section numbering, a toc tree with ``:numbered:``

    """
    doc = apply_filter(source, dry_run=True)  # type: pf.Doc

    # if the ipypublish options are not already in the metadata add them
    if "ipub" not in doc.metadata:
        doc.metadata["ipub"] = pf.MetaMap()
    if "use_numref" not in doc.metadata["ipub"]:
        doc.metadata["ipub"]["use_numref"] = pf.MetaBool(use_numref)
    if "at_notation" not in doc.metadata["ipub"]:
        doc.metadata["ipub"]["at_notation"] = pf.MetaBool(at_notation)
    if "reftag" not in doc.metadata["ipub"]:
        doc.metadata["ipub"]["reftag"] = pf.MetaString(reftag)

    out_str = apply_filter(doc,
                           [
                               prepare_cites.main,
                               prepare_labels.main,
                               prepare_raw.main,
                               format_cite_elements.main,
                               format_raw_spans.main,
                               format_label_elements.main
                           ],
                           out_format=to_format,
                           in_format=from_format,
                           # strip_meta=True TODO should this be done?
                           )
    if strip:
        out_str = out_str.strip()

    return out_str
