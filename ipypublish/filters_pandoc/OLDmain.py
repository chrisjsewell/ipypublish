"""pandoc filters used in converting markdown to a target format

initially adapted from nbconvert/filters/filter_links.py

Other sources of information:

- [Pandoc User Guide](https://pandoc.org/MANUAL.html#citations)
- [List of Pandoc Elements](https://metacpan.org/pod/Pandoc::Elements)
- [reStructuredText Primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [reStructuredText Directives](http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure)
- [sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html)

.. note:: 

    could use panflute, for more pythonic API, however,
    and using pandocxnos written in 

"""
import json

from pandocfilters import (toJSONFilters, walk)

from ipypublish.filters_pandoc.utils import ElementTypes as el

from ipypublish.filters_pandoc.utils import (convert_pandoc, compare_version,
                                             get_api_version)
from ipypublish.filters_pandoc.OLDformat_conversion import (
    latex2rst, resolve_references_filter
)
from ipypublish.filters_pandoc.OLDxnos import (
    attach_attrs_factory, attach_attrs_table_filter, detach_attrs_factory,
    extract_image_attrs, resolve_math_filter,
    resolve_figures_filter, resolve_tables_filter
)


def pandoc_filters():
    """ run a set of ipypublish pandoc filters directly on the pandoc AST,
    via ``pandoc --filter ipubpandoc``
    """
    filters = gather_required_filters()
    toJSONFilters(filters)


def jinja_filter(source, to_format, from_format="markdown",
                 extra_args=None,
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
    extra_args: list[str]
        extra arguments to parse to pandoc
    at_notation: bool
        interpret @label as a reference type based on its prefix modifier,
        latex: '' = cite '+' = cref,    '^' = Cref,    '!' = ref,  '=' = eqref
        rst: '' = :cite: '+' = :numref: '^' = :numref: '!' = :ref: '=' = :eq:
        also works with multi labels, e.g. ![@{ref1,ref2}]
    reftag: str
        latex tag for references, when converting [](#label) -> \\ref{label}
    use_numref: bool
        whether to use the ``:numref:`` directive or just ``:ref:``

    Notes
    -----

    if ``at_notation``, ``reftag``, ``use_numref`` set in the source metadata,
    under key ``ipub``, this will preferentially be used.
    See https://pandoc.org/MANUAL.html#metadata-blocks, e.g.

    .. code-block:: yaml

        ---
        ipub:
            use_numref: True
        ---

    ``:numref:`` requires ``numfig = True`` in conf.py and,
    for section numbering, a toc tree with ``:numbered:``

    """
    # convert to pandoc's JSON structure
    jsonstr = convert_pandoc(source, from_format, 'json',
                             extra_args=extra_args)
    doc = json.loads(jsonstr)

    # extract metadata
    if 'meta' in doc:
        meta = doc['meta']
    elif doc[0]:  # old API
        meta = doc[0]['unMeta']
    else:
        meta = {}

    # if the ipypublish options are not already in the metadata add them
    meta.setdefault("ipub", {"t": "MetaMap", "c": {}})
    meta["ipub"]["c"].setdefault(
        "use_numref", {"t": "MetaBool", "c": use_numref})
    meta["ipub"]["c"].setdefault(
        "at_notation", {"t": "MetaBool", "c": at_notation})
    meta["ipub"]["c"].setdefault(
        "reftag", {"t": "MetaInlines",
                   "c": [{"t": "Str", "c": reftag}]})
    if get_api_version(doc) is not None:
        meta["ipub"]["c"].setdefault(
            "pandoc_api", {
                "t": "MetaInlines",
                "c": [{"t": "Str",
                       "c": get_api_version(doc)}]})

    # gather all required filters
    filters = gather_required_filters()

    # Walk through the JSON structure and apply filters
    for flter in filters:
        doc = walk(doc, flter, to_format, meta)

    return convert_pandoc(json.dumps(doc), 'json', to_format)


def gather_required_filters():
    """gather the set of required filters """

    filters = []

    # replace latex tags with rst
    filters.append(latex2rst)

    # resolve references
    filters.append(resolve_references_filter)

    # resolve math
    filters.extend([
        attach_attrs_factory(el.Math, allow_space=True),
        resolve_math_filter,
        detach_attrs_factory(el.Math),
    ])

    # resolve images
    if compare_version('1.16', '>='):
        filters.append(resolve_figures_filter)
    else:
        filters.extend([
            attach_attrs_factory(el.Image,
                                 extract_attrs=extract_image_attrs),
            resolve_figures_filter,
            detach_attrs_factory(el.Image)
        ])

    # resolve tables
    filters.extend([
        attach_attrs_table_filter,
        resolve_tables_filter,
        detach_attrs_factory(el.Table),
    ])

    return filters
