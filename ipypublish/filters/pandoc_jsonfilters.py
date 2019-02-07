"""pandoc filters used in converting markdown cells to latex.
Usage in jinja template:

    convert_pandoc('markdown', 'json') | pandoc_jsonfilters(at_notation=True) | convert_pandoc('json','latex')  # noqa: E501

initially adapted from nbconvert/filters/filter_links.py

Other sources of information:

- [Pandoc User Guide](https://pandoc.org/MANUAL.html#citations)
- [List of Pandoc Elements](https://metacpan.org/pod/Pandoc::Elements)
- [reStructuredText Primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [reStructuredText Directives](http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure)
- [sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html)


NOTE could use panflute, for more pythonic API, however,
it only supports ``pandoc >= 1.17``

"""

import re
import sys
import json

from distutils.util import strtobool
from pandocfilters import (applyJSONFilters,  # noqa: F401
                           RawInline, Math, Image, Table, RawBlock)
# TODO at present we defer import, so we can monkey patch stdin during tests
# from pandocxnos import (elt, PandocAttributes,
#                         attach_attrs_factory, detach_attrs_factory,
#                         extract_attrs)
# from pandocxnos import init as get_pandoc_version
# from nbconvert.utils.pandoc import get_pandoc_version
# from nbconvert.filters.latex import escape_latex
from nbconvert.utils.pandoc import pandoc

if sys.version_info > (3,):
    from urllib.request import unquote  # pylint: disable=no-name-in-module
else:
    from urllib import unquote  # pylint: disable=no-name-in-module


LATEX_FIG_LABELLED = """\\begin{{figure}}[{options}]
\\hypertarget{{{label}}}{{%
\\begin{{center}}
\\adjustimage{{max size={{0.9\\linewidth}}{{0.9\\paperheight}},{size}}}{{{path}}}
\\end{{center}}
\\caption{{{caption}}}\\label{{{label}}}
}}
\\end{{figure}}"""  # noqa: E501

LATEX_FIG_UNLABELLED = """\\begin{{figure}}[{options}]
\\begin{{center}}
\\adjustimage{{max size={{0.9\\linewidth}}{{0.9\\paperheight}},{size}}}{{{path}}}
\\end{{center}}
\\caption{{{caption}}}
\\end{{figure}}"""  # noqa: E501


def pandoc_jsonfilters(source, out="latex", at_notation=True,
                       reftag="cref", use_numref=True):
    """
    Apply filters to the pandoc json object to convert it to required type

    Parameters
    ----------
    source: str
        content in the form of a string encoded JSON object,
        as represented internally in ``pandoc``
    to: str
        latex or rst
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

    ``:numref:`` requires ``numfig = True`` in conf.py and,
    for section numbering, a toc tree with ``:numbered:``

    """
    if out not in ["latex", "rst"]:
        raise AssertionError("conversion must be to 'latex' or 'rst'")

    from pandocxnos import (elt,
                            attach_attrs_factory, detach_attrs_factory)
    from pandocxnos import init as get_pandoc_version
    # TODO is there a better way to get the pandoc-api-version
    api_version = None
    if get_pandoc_version() >= '1.18':
        source_json = json.loads(source)
        api_version = source_json.get("pandoc-api-version", None)

    global Image
    if get_pandoc_version() < '1.16':
        Image = elt('Image', 2)

    filters = []

    # replace latex tags with rst
    if out == "rst":
        filters.append(_replace_latex2rst(use_numref=use_numref))

    # resolve references
    filters.append(_resolve_one_ref_func(out, cmnd=reftag,
                                         use_at_notation=at_notation,
                                         use_numref=use_numref))
    # resolve math
    filters.extend([
        attach_attrs_factory(Math, allow_space=True),
        _resolve_math(out),
        detach_attrs_factory(Math),
    ])
    # resolve images
    if get_pandoc_version() >= '1.16':
        filters.append(_resolve_figures_func(out, api_version))
    else:
        filters.extend([
            attach_attrs_factory(Image,
                                 extract_attrs=_extract_image_attrs),
            _resolve_figures_func(out, api_version),
            detach_attrs_factory(Image)
        ])
    # resolve tables
    filters.extend([
        _attach_attrs_table,
        _resolve_tables_func(out, api_version),
        detach_attrs_factory(Table),
    ])

    return applyJSONFilters(filters, source)

# TODO sphinx directives (like todo, warning etc...) to latex


def _replace_latex2rst(use_numref=True):
    def replace_latex2rst(key, value, fmt, meta):
        """attempt to replace latex tags with rst directives"""
        numref = "numref" if use_numref else "ref"

        if ((key == 'RawInline' or key == 'RawBlock') and
                (value[0] == 'tex' or value[0] == 'latex')):

            match_noopts = re.match(
                r"^\s*\\([^\{\[]+)\{([^\}]+)\}\s*$", value[1])
            if match_noopts:
                tag = match_noopts.group(1)
                label = match_noopts.group(2)
                rst_dir = {"cref": ":{numref}:`{label}`",
                           "Cref": ":{numref}:`{label}`",
                           "ref": ":ref:`{label}`",
                           "cite": " :cite:`{label}` ",
                           "todo": "\n\n.. todo:: {label}\n\n",
                           }.get(tag, None)
                if rst_dir:
                    if key == 'RawInline':
                        return RawInline(
                            'rst', rst_dir.format(label=label, numref=numref))
                    else:
                        return RawBlock(
                            'rst', rst_dir.format(label=label, numref=numref))

            match_wopts = re.match(
                r"^\s*\\([^\{\[]+)\[([^\]]*)\]\{([^\}]+)\}\s*$", value[1])
            if match_wopts:
                tag = match_wopts.group(1)
                options = match_wopts.group(2)
                label = match_wopts.group(3)
                rst_dir = {
                    "todo": "\n\n.. todo:: {label}\n\n",
                }.get(tag, None)
                if rst_dir:
                    if key == 'RawInline':
                        return RawInline(
                            'rst',
                            rst_dir.format(label=label, options=options))
                    else:
                        return RawBlock(
                            'rst',
                            rst_dir.format(label=label, options=options))

    return replace_latex2rst


def _sanitize_label(label):
    """from pandoc documentation
    The citation key must begin with a letter, digit, or _,
    and may contain alphanumerics, _,
    and internal punctuation characters (:.#$%&-+?<>~/)
    """
    label = str(label).lower()
    label = re.sub("[^a-zA-Z0-9-:\\.]+", "", label)
    # TODO raise warning if changed?
    return label


def _extract_image_attrs(x, n):
    """Extracts attributes for an image.  n is the index where the
    attributes begin.  Extracted elements are deleted from the element
    list x.  Attrs are returned in pandoc format.
    """
    from pandocxnos import extract_attrs, PandocAttributes
    from pandocxnos import init as get_pandoc_version
    try:
        return extract_attrs(x, n)

    except (ValueError, IndexError):

        if get_pandoc_version() < '1.16':
            # Look for attributes attached to the image path, as occurs with
            # image references for pandoc < 1.16 (pandoc-fignos Issue #14).
            # See http://pandoc.org/MANUAL.html#images for the syntax.
            # Note: This code does not handle the "optional title" for
            # image references (search for link_attributes in pandoc's docs).
            assert x[n-1]['t'] == 'Image'
            image = x[n-1]
            s = image['c'][-1][0]
            if '%20%7B' in s:
                path = s[:s.index('%20%7B')]
                attrs = unquote(s[s.index('%7B'):])
                image['c'][-1][0] = path  # Remove attr string from the path
                return PandocAttributes(attrs.strip(), 'markdown').to_pandoc()
        raise


def _attach_attrs_table(key, value, fmt, meta):
    """Extracts attributes and attaches them to element.

    We can't use attach_attrs_factory() because Table is a block-level element
    """
    from pandocxnos import extract_attrs
    if key in ['Table']:
        assert len(value) == 5
        caption = value[0]  # caption, align, x, head, body

        # Set n to the index where the attributes start
        n = 0
        while n < len(caption) and not \
                (caption[n]['t'] == 'Str' and caption[n]['c'].startswith('{')):
            n += 1

        try:
            attrs = extract_attrs(caption, n)
            value.insert(0, attrs)
        except (ValueError, IndexError):
            pass


def _resolve_one_ref_func(out="latex", use_at_notation=False,
                          cmnd="cref", prefix="", use_numref=True):

    def resolve_one_reference(key, value, format, meta):
        """ takes a tuple of arguments that are compatible with
        ``pandocfilters.walk()`` that allows identifying hyperlinks in the
        document and transforms them into valid LaTeX
        calls so that linking to headers between cells is possible.

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        format: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        # replace markdown references with latex ones
        if key == 'Link':
            target = value[-1][0]  # in older pandoc, no attributes at front
            m = re.match(r'#(.+)$', target)
            if m:
                # pandoc automatically makes labels for headings.
                label = _sanitize_label(m.group(1))
                if out == "latex":
                    return RawInline(
                        'tex', '{0}\\{1}{{{2}}}'.format(prefix, cmnd, label))
                elif out == "rst":
                    # RawInline('rst', ":ref:``".format(label))
                    # TODO link vs ref?
                    return None

        # replace html style citations; <cite data-cite="cite_key"></cite>
        # TODO this does not remove any content between the start-end tags
        if key == 'RawInline' and value[0] == 'html':
            if re.match(r"^\s*</cite>\s*$", value[1]):
                return []  # remove
            match = re.match(
                r"<cite\s*data-cite\s*=\"?([^>\"]*)\"?>", value[1])
            if not match:
                return None
            key = match.group(1)
            if not key:
                return []
            if out == "latex":
                return RawInline('tex', "\\cite{{{0}}}".format(key))
            if out == "rst":
                return RawInline('rst', " :cite:`{0}` ".format(key))
                # NB citations must have space at either side to be resolved

        # replace @label style references
        if use_at_notation:
            # References may occur in a variety of places; we must process them
            # all.
            if key in ['Para', 'Plain']:
                _process_at_refs(value, out, use_numref)
            elif key == 'Image':
                _process_at_refs(value[-2], out, use_numref)
            elif key == 'Table':
                _process_at_refs(value[-5], out, use_numref)
            elif key == 'Span':
                _process_at_refs(value[-1], out, use_numref)
            elif key == 'Emph':
                _process_at_refs(value, out, use_numref)
            elif key == 'Strong':
                _process_at_refs(value, out, use_numref)

        return None

    return resolve_one_reference


def _process_at_refs(el, out="latex", use_numref=True):
    # NOTE in pandoc-xnos they repair_refs for
    # "-f markdown+autolink_bare_uris" with pandoc < 1.18
    numref = "numref" if use_numref else "ref"

    deletions = []
    for i, sub_el in enumerate(el):
        if sub_el['t'] == 'Cite' and len(sub_el['c']) == 2:
            citations = sub_el['c'][0]
            # extracts the */+/! modifier in front of the Cite
            modifier = None
            if el[i-1]['t'] == 'Str':
                modifier = el[i - 1]['c'][-1]
                if modifier in ['^', '+', '!', '=']:
                    if len(el[i - 1]['c']) > 1:
                        # Cut the modifier off of the string
                        el[i-1]['c'] = el[i-1]['c'][:-1]
                    else:
                        # The element contains only the modifier; delete it
                        deletions.append(i-1)

            labels = [citation["citationId"] for citation in citations]

            if out == "latex":
                tag = {'+': 'cref', '^': "Cref", "!": "ref", "=": "eqref",
                       }.get(modifier, 'cite')
                if tag in ["ref", "eqref"] and len(citations) > 1:
                    tex = (
                        ", ".join(['\\{0}{{{1}}}'.format(tag, l)
                                   for l in labels[:-1]]) +
                        ' and \\{0}{{{1}}}'.format(tag, labels[-1]))
                else:
                    tex = '\\{0}{{{1}}}'.format(tag, ",".join(labels))

                el[i] = RawInline('tex', tex)

            if out == "rst":
                tag = {'+': numref, '^': numref, "!": "ref", "=": "eq",
                       }.get(modifier, 'cite')
                if tag == "cite":
                    rst = ' :{0}:`{1}` '.format(tag, ",".join(labels))
                    # NB citations must have space either side to be resolved
                elif len(citations) == 1:
                    rst = ':{0}:`{1}`'.format(tag, ",".join(labels))
                else:
                    rst = (
                        ",".join([':{0}:`{1}`'.format(tag, l)
                                  for l in labels[:-1]]) +
                        ' and :{0}:`{1}`'.format(tag, labels[-1]))

                el[i] = RawInline('rst', rst)

    # delete in place
    deleted = 0
    for delete in deletions:
        del el[delete - deleted]
        deleted += 1


def _resolve_math(out="latex"):
    def resolve_math(key, value, format, meta):
        """ see https://github.com/tomduck/pandoc-eqnos/blob/master/pandoc_eqnos.py

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        format: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        if key == 'Math' and len(value) == 3:

            body = value[-1]
            # mtype = value[1]
            # # e.g. {'t': 'InlineMath'} or {'t': 'DisplayMath'}
            attributes = value[0]
            label = attributes[0]
            keywords = dict(attributes[-1])

            if label and out == "latex":
                label_tag = "\\label{{{0}}}".format(label)
            else:
                label_tag = ""
            env = keywords.get('env', 'equation')
            numbered = '' if strtobool(
                keywords.get('numbered', 'true')) else '*'
            tex = '\\begin{{{0}{1}}}{2}{3}\\end{{{0}{1}}}'.format(
                env, numbered, body, label_tag)

            if out == "latex":
                return RawInline('tex', tex)
            elif out == "rst":
                if not label:
                    return RawInline(
                        'rst',
                        '\n\n.. math::\n   :nowrap:\n\n   {0}\n\n'.format(tex))
                return RawInline(
                    'rst', '\n\n.. math::\n   :nowrap:\n   :label: {0}'
                    '\n\n   {1}\n\n'.format(label, tex))

    return resolve_math


def _convert_scale(string, out_units):
    match = re.compile(
        "^\\s*([0-9]+\\.?[0-9]*)([a-z\\%]*)\\s*$").match(str(string))
    if match is None:
        raise ValueError(
            "string could not be resolved as a value: {}".format(string))
    value = float(match.group(1))
    in_units = match.group(2)
    in_units = "fraction" if not in_units else in_units

    if in_units == out_units:
        return value

    convert = {
        ("%", "fraction"): lambda x: x / 100.,
        ("fraction", "%"): lambda x: x*100.
    }.get((in_units, out_units), None)

    if convert is None:
        raise ValueError("could not find a conversion for "
                         "{0} to {1}: {2}".format(in_units, out_units, string))

    return convert(value)


def _resolve_figures_func(out="latex", api_version=None):
    def resolve_figures(key, value, fmt, meta):
        """ see https://github.com/tomduck/pandoc-eqnos/

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        fmt: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        from pandocxnos import init as get_pandoc_version
        if key == 'Para' and len(value) == 1 and value[0]['t'] == 'Image':
            if len(value[0]['c']) == 2:  # Unattributed, bail out
                return None
            attributes, caption_block = value[0]['c'][:2]
            path, typef = value[0]['c'][2]  # TODO is typef always 'fig:'?
            label = _sanitize_label(attributes[0])
            keywords = dict(attributes[-1])

            if not out == "latex":
                return None
                # TODO rst figure, all works except convert width/height to %

            # convert the caption to latex
            if get_pandoc_version() >= '1.18':
                caption_json = json.dumps(
                    {
                        "blocks": [{"t": "Para", "c": caption_block}],
                        "meta": meta,
                        "pandoc-api-version": api_version
                    })
            else:
                caption_json = json.dumps(
                    [{'unMeta': {}},
                     [{"t": "Para", "c": caption_block}]])
            caption = pandoc(caption_json, 'json', 'latex')

            options = keywords.get("placement", "")
            size = ''
            if "width" in keywords:
                width = _convert_scale(keywords['width'], "fraction")
                size = 'width={0}\\linewidth'.format(width)
            elif "height" in keywords:
                height = _convert_scale(keywords['height'], "fraction")
                size = 'height={0}\\paperheight'.format(height)

            if label:
                latex = LATEX_FIG_LABELLED.format(
                    label=label,
                    options=options,
                    path=path,
                    caption=caption,
                    size=size)
            else:
                latex = LATEX_FIG_UNLABELLED.format(
                    options=options,
                    path=path,
                    caption=caption,
                    size=size)

            return {"t": "Para", "c": [RawInline('tex', latex)]}

    return resolve_figures


def _resolve_tables_func(out="latex", api_version=None):
    def resolve_tables(key, value, fmt, meta):
        """ see https://github.com/tomduck/pandoc-tablenos

        Parameters
        ----------
        key: str
            the type of the pandoc object (e.g. 'Str', 'Para')
        value:
            the contents of the object (e.g. a string for 'Str', a list of
            inline elements for 'Para')
        fmt: str
            is the target output format (as supplied by the
            `format` argument of `walk`)
        meta:
            is the document's metadata

        Returns
        -------
        pandoc_object:

        """
        from pandocxnos import elt
        AttrTable = elt('Table', 6)

        if key == 'Table':
            if len(value) == 5:  # Unattributed, bail out
                return None
            attributes, caption = value[:2]
            label = _sanitize_label(attributes[0])

            if out == "latex":
                value[1] += [RawInline('tex', '\\label{{{0}}}'.format(label))]
                return [AttrTable(*value)]

            elif out == "rst":
                rst_label = RawInline('rst', '\n.. _`{0}`:\n\n'.format(label))
                return [{"t": "Para", "c": [rst_label]}, AttrTable(*value)]

    return resolve_tables
