""" filters which utilize pandocxnos
"""
import sys
import re
import json
import warnings

from distutils.util import strtobool

from ipypublish.filters_pandoc.utils import ElementTypes as el
from ipypublish.filters_pandoc.utils import (
    traverse_meta, sanitize_label, compare_version, convert_pandoc
    )

# TODO at present we defer import, so we can monkey patch stdin during tests
# from pandocxnos import (elt, PandocAttributes,
#                         attach_attrs_factory, detach_attrs_factory,
#                         extract_attrs)

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


def attach_attrs_factory(*args, **kwargs):
    """Returns attach_attrs(key, value, fmt, meta) action that reads and
    attaches attributes to unattributed elements generated by the
    pandocfilters function f (e.g. pandocfilters.Math, etc).

    The extract_attrs() function should read the attributes and raise a
    ValueError or IndexError if attributes are not found.
    """
    from pandocxnos import attach_attrs_factory
    return attach_attrs_factory(*args, **kwargs)


def detach_attrs_factory(*args, **kwargs):
    """Returns detach_attrs(key, value, fmt, meta) action that detaches
    attributes attached to elements of type f (e.g. pandocfilters.Math, etc).
    Attributes provided natively by pandoc will be left as is."""
    from pandocxnos import detach_attrs_factory
    return detach_attrs_factory(*args, **kwargs)


def attach_attrs_table_filter(key, value, fmt, meta):
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


def extract_image_attrs(x, n):
    """Extracts attributes for an image.  n is the index where the
    attributes begin.  Extracted elements are deleted from the element
    list x.  Attrs are returned in pandoc format.
    """
    from pandocxnos import extract_attrs, PandocAttributes
    try:
        return extract_attrs(x, n)

    except (ValueError, IndexError):

        if compare_version('1.16', '<'):
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


def resolve_math_filter(key, value, fmt, meta):
    """ see https://github.com/tomduck/pandoc-eqnos/blob/master/pandoc_eqnos.py

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

    """
    # if the MATH element has been marked with attributes
    if key == 'Math' and len(value) == 3:

        body = value[-1]
        # mtype = value[1]
        # # e.g. {'t': 'InlineMath'} or {'t': 'DisplayMath'}
        attributes = value[0]
        label = attributes[0]
        keywords = dict(attributes[-1])

        # create latex representation of the equation
        if label and fmt == "latex":
            label_tag = "\\label{{{0}}}".format(label)
        else:
            label_tag = ""
        env = keywords.get('env', 'equation')
        numbered = '' if strtobool(
            keywords.get('numbered', 'true')) else '*'
        tex = '\\begin{{{0}{1}}}{2}{3}\\end{{{0}{1}}}'.format(
            env, numbered, body, label_tag)

        if fmt == "latex":
            return el.RawInline('tex', tex)
        elif fmt == "rst":
            if not label:
                return el.RawInline(
                    'rst',
                    '\n\n.. math::\n   :nowrap:\n\n   {0}\n\n'.format(tex))
            return el.RawInline(
                'rst', '\n\n.. math::\n   :nowrap:\n   :label: {0}'
                '\n\n   {1}\n\n'.format(label, tex))


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


def resolve_figures_filter(key, value, fmt, meta):
    """ see https://github.com/tomduck/pandoc-eqnos/

    NB: for latex fmt, to convert captions, a 'pandoc_api' key 
    is required in the metadata of the form '1.2.3.4'

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

    """
    api_version, _ = traverse_meta(meta, ["pandoc_api", 0],
                                   assert_type="Str")

    if api_version is None:
        api_version, _ = traverse_meta(meta, ["ipub", "pandoc_api", 0],
                                       assert_type="Str")

    if key == 'Para' and len(value) == 1 and value[0]['t'] == 'Image':
        if len(value[0]['c']) == 2:  # Unattributed, bail out
            return None
        attributes, caption_block = value[0]['c'][:2]
        path, typef = value[0]['c'][2]  # TODO is typef always 'fig:'?
        label = sanitize_label(attributes[0])
        keywords = dict(attributes[-1])

        if fmt == "latex":

            # convert the caption to latex
            # TODO is there a better way to do this
            caption_json = None
            if compare_version('1.18', '>=') and api_version:
                caption_json = json.dumps(
                    {
                        "blocks": [{"t": "Para", "c": caption_block}],
                        "meta": meta,
                        "pandoc-api-version": [
                            int(s) for s in api_version.strip().split(".")]
                    })
            elif compare_version('1.18', '>='):
                warnings.warn("'pandoc_api' was not set in the metadata, "
                              "so cannot convert caption")
            else:  # old API
                caption_json = json.dumps(
                    [{'unMeta': {}},
                        [{"t": "Para", "c": caption_block}]])

            if caption_json is not None:
                try:
                    caption = convert_pandoc(caption_json, 'json', 'latex')
                except RuntimeError as err:
                    raise ValueError(
                        "could not convert the pandoc block containing a "
                        "caption: {}\n{}".format(caption_json, err))
            else:
                caption = ""

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

            return {"t": "Para", "c": [el.RawInline('tex', latex)]}

        elif fmt == "rst":
            # TODO rst figure, all works except convert width/height to %
            return None


def resolve_tables_filter(key, value, fmt, meta):
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

    """
    if key == 'Table':
        if len(value) == 5:  # Unattributed, bail out
            return None
        attributes, caption = value[:2]
        label = sanitize_label(attributes[0])

        if fmt == "latex":
            value[1] += [el.RawInline('tex', '\\label{{{0}}}'.format(label))]
            return [el.AttrTable(*value)]

        elif fmt == "rst":
            rst_label = el.RawInline('rst', '\n.. _`{0}`:\n\n'.format(label))
            return [{"t": "Para", "c": [rst_label]}, el.AttrTable(*value)]
