from nbconvert.utils.pandoc import (get_pandoc_version, check_pandoc_version,
                                    cast_bytes)
from pandocfilters import elt as _elt
from six import string_types
from distutils.version import LooseVersion
import warnings
import re
from io import TextIOWrapper, BytesIO
import subprocess
import io
import json
from collections import OrderedDict
import panflute as pf

from panflute import Element, Doc  # noqa: F401
from types import FunctionType  # noqa: F401


def apply_filter(in_object, filter_func=None,
                 out_format="panflute", in_format="markdown",
                 strip_meta=False, strip_blank_lines=False,
                 replace_api_version=True, dry_run=False,
                 **kwargs):
    # type: (list[str], FunctionType) -> str
    """convenience function to apply a panflute filter(s) 
    to a string, list of string lines, pandoc AST or panflute.Doc

    Parameters
    ----------
    in_object: str or list[str] or dict
        can also be panflute.Doc
    filter_func:
        the filter function or a list of filter functions
    out_format: str
        for use by pandoc or, if 'panflute', return the panflute.Doc
    in_format="markdown": str
    strip_meta=False: bool
        strip the document metadata before final conversion
    strip_blank_lines: bool
    strip_ends: bool
        strip any blank lines or space from the start and end
    replace_api_version: bool
        for dict input only, if True,
        find the api_version of the available pandoc and
        reformat the json as appropriate
    dry_run: bool
        If True, return the Doc object, before applying the filter
    kwargs:
        to parse to filter func

    Returns
    -------
    str

    """
    if isinstance(in_object, pf.Doc):
        pass
    elif isinstance(in_object, dict):
        if not in_format == "json":
            raise AssertionError("the in_format for a dict should be json, "
                                 "not {}".format(in_format))
        if "meta" not in in_object:
            raise ValueError(
                "the in_object does contain a 'meta' key")
        if "blocks" not in in_object:
            raise ValueError(
                "the in_object does contain a 'blocks' key")
        if "pandoc-api-version" not in in_object:
            raise ValueError(
                "the in_object does contain a 'pandoc-api-version' key")
        if replace_api_version:
            # run pandoc on a null object, to get the correct api version
            null_raw = pf.run_pandoc("", args=["-t", "json"])
            null_stream = io.StringIO(null_raw)
            api_version = pf.load(null_stream).api_version

            # see panflute.load, w.r.t to legacy version
            if api_version is None:
                in_object = [{'unMeta': in_object["meta"]},
                             in_object["blocks"]]
            else:
                ans = OrderedDict()
                ans['pandoc-api-version'] = api_version
                ans['meta'] = in_object["meta"]
                ans['blocks'] = in_object["blocks"]
                in_object = ans
        in_str = json.dumps(in_object)
    elif isinstance(in_object, (list, tuple)):
        in_str = "\n".join(in_object)
    elif isinstance(in_object, string_types):
        in_str = in_object
    else:
        raise TypeError("object not accepted: {}".format(in_object))

    if not isinstance(in_object, pf.Doc):
        in_json = pf.run_pandoc(in_str,
                                ["-f", in_format, "-t", "json"])
        f = io.StringIO(in_json)
        doc = pf.load(f)
    else:
        doc = in_object

    doc.format = out_format

    if dry_run:
        return doc

    if not isinstance(filter_func, (list, tuple, set)):
        filter_func = [filter_func]

    out_doc = doc
    for func in filter_func:
        out_doc = func(out_doc, **kwargs)  # type: Doc

    # post-process Doc
    if strip_meta:
        out_doc.metadata = {}
    if out_format == "panflute":
        return out_doc

    # create out str
    with io.StringIO() as f:
        pf.dump(doc, f)
        jsonstr = f.getvalue()
    # jsonstr = json.dumps(out_doc.to_json()
    out_str = pf.run_pandoc(jsonstr,
                            ["-f", "json", "-t", out_format])

    # post-process final str
    if strip_blank_lines:
        out_str = out_str.replace("\n\n", "\n")

    return out_str


def strip_quotes(string):
    # type: (str) -> str
    if string.startswith("'") and string.endswith("'"):
        string = string[1:-1]
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string


def process_attributes(attr_string):
    """process a string of classes and attributes, 
    e.g. '.class-name .other a=1 b="some text"' will be returned as:
    ["class-name", "other"], {"a": 1, "b": "some text"}

    Returns:
    list: classes
    dict: attributes
    """
    # find classes, denoted by .class-name
    classes = [c[1][1:] for c in re.findall('(^|\s)(\\.[\\-\\_a-zA-Z]+)',
                                            attr_string)]
    # find attributes, denoted by a=b, respecting quotes
    attr = {c[1]: strip_quotes(c[2]) for c in re.findall(
        '(^|\s)([\\-\\_a-zA-Z]+)\s*=\s*(\\".+\\"|\\\'.+\\\'|[^\s\\"\\\']+)',
        attr_string)}
    # TODO this generally works, but should be stricter against any weird
    # fringe cases
    # TODO add tests
    return classes, attr


def convert_units(string, out_units):
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


# TODO DELETE ALL BELOW HERE

def convert_pandoc(source, fmt, to, extra_args=None, encoding='utf-8',
                   allow_stderr=False):
    """Convert an input string using pandoc.

    Pandoc converts an input string `from` a format `to` a target format.

    This is copied from nbconvert, but raises an exception if pandoc fails,
    rather than failing silently

    Parameters
    ----------
    source : string
      Input string, assumed to be valid format `from`.
    fmt : string
      The name of the input format (markdown, etc.)
    to : string
      The name of the output format (html, etc.)

    Returns
    -------
    out : str
      Output as returned by pandoc.

    Raises
    ------
    nbconvert.pandoc.PandocMissing
      If pandoc is not installed.
    RuntimeError
      If allow_stderr=False and stderr returned from pandoc is not empty

    Any error messages generated by pandoc are printed to stderr.

    """
    cmd = ['pandoc', '-f', fmt, '-t', to]
    if extra_args:
        cmd.extend(extra_args)

    # this will raise an exception that will pop us out of here
    check_pandoc_version()

    # we can safely continue
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(cast_bytes(source, encoding))
    stdout = TextIOWrapper(BytesIO(stdout), encoding, 'replace').read()
    stderr = TextIOWrapper(BytesIO(stderr), encoding, 'replace').read()
    if stderr:
        raise RuntimeError("pandoc run failed: {}".format(stderr))

    return stdout.rstrip('\n')


def compare_version(target, comparison):
    """Set docstring here.

    Parameters
    ----------
    target: str
        target version of pandoc
    comparison: str
        one of '>', '<', '<=', '>=', '=='

    Returns
    -------
    bool

    """
    # TODO this only works if you are
    # converting json in the same environment
    # from pandocxnos import init as get_pandoc_version
    version = LooseVersion(get_pandoc_version())
    required = LooseVersion(target)
    if comparison == ">=":
        return version >= required
    elif comparison == "<=":
        return version <= required
    elif comparison == ">":
        return version > required
    elif comparison == "<":
        return version < required
    elif comparison == "==":
        return version == required
    else:
        raise ValueError("comparison not recognised: {}".format(comparison))


def get_api_version(source_json, as_str=True):
    """
    return None if not found
    if as_str=True return '1.2.3' else return [1, 2, 3]
    """
    # TODO is there a better way to get the pandoc-api-version
    api_version = None
    if compare_version('1.18', '>='):
        try:
            api_version = source_json.get("pandoc-api-version", None)
        except Exception as err:
            warnings.warn("could not extract pandoc-api-version "
                          "from source: {}".format(err))

    if api_version is not None and as_str:
        return ".".join([str(i) for i in api_version])
    return api_version


def traverse_meta(meta, keypath, return_missing=(None, None),
                  assert_type=None):
    """traverse pandoc json meta 

    Parameters
    ----------
    meta: dict
    keypath: list
        path to traverse. if the last key is an integer, 
        then return that index of a "MetaInlines"
    return_missing=None: 
        what to return if the keypath is not found
    assert_type=None: str or None
        if not None, assert the returned object has a particular pandoc type

    Returns
    -------
    pvalue: object
        the value of the pandoc node
    ptype: str
        the type of the pandoc node

    """
    obj = _traverse_meta(meta, keypath, return_missing, assert_type)
    if obj == return_missing:
        return obj
    else:
        return obj["c"], obj["t"]


def _traverse_meta(meta, keypath, return_missing=(None, None),
                   assert_type=None):
    """see traverse_meta"""
    final_index = None
    if isinstance(keypath[-1], int):
        final_index = keypath.pop(-1)

    for i, key in enumerate(keypath):
        if not isinstance(key, string_types):
            raise TypeError("key must be a string: {}".format(key))
        if i == 0 and key not in meta:
            return return_missing
        elif i != 0 and meta["t"] != "MetaMap":
            return return_missing
        elif i != 0 and key not in meta["c"]:
            return return_missing

        if i == 0:
            meta = meta[key]
        else:
            meta = meta["c"][key]

    if final_index is not None:
        if meta["t"] != "MetaInlines":
            return return_missing
        meta = meta["c"][final_index]

    if assert_type is not None and assert_type != meta["t"]:
        raise ValueError(
            "the metadata from {0} is {1} instead of {2}".format(
                keypath, meta["t"], assert_type
            ))

    return meta


def add_to_meta(meta, keypath, value, allow_overwrite=False):

    if not all([isinstance(k, string_types) for k in keypath]):
        raise TypeError(
            "keypath contains non-string items: {}".format(keypath))

    # if traverse_meta(meta, keypath, return_missing=None) is not None:
    #     if not allow_overwrite:
    #         raise ValueError("keypath already exists: {}".format(keypath))

    subpath = keypath[:]
    existing_metamap = None
    while subpath:
        obj = _traverse_meta(meta, subpath, return_missing=None)
        if obj is not None:
            if obj["t"] != "MetaMap":
                raise ValueError(
                    "subpath terminates with {}: {}".format(obj["t"], subpath))
            existing_metamap = obj
            break
        subpath = subpath[:-1]

    # keys_to_add = keypath[len(subpath):]

    # new_meta_map = construct_nested_metamap(keys_to_add, value)

    if not existing_metamap:
        meta[keypath[0]] = construct_metamap(keypath[1:], value)
    else:
        root_key = keypath[len(subpath) - 1]
        new_path = keypath[len(subpath):]
        existing_metamap['c'][root_key] = construct_metamap(new_path, value)


def construct_metamap(keypath, value):
    """construct a nested metamap from a key path and value"""
    if not keypath:
        return construct_meta_element(value)

    new_meta = {'t': 'MetaMap', 'c': {}}
    sub_meta = new_meta
    final_key = keypath[-1]
    for key in keypath[:-1]:
        new_meta['c'][key] = {'t': 'MetaMap', 'c': {}}
        sub_meta = new_meta['c'][key]
    sub_meta['c'][final_key] = construct_meta_element(value)


def construct_meta_element(value):
    """constuct a meta element, based on the type of the value"""
    if isinstance(value, string_types) or isinstance(value, (int, float)):
        return {
            "t": "MetaInlines",
            "c": [{"t": "Str", "c": str(value)}]
        }
    elif isinstance(value, bool):
        return {"t": "MetaBool", "c": value}
    elif (isinstance(value, (tuple, list, set)) and
          all([isinstance(v, string_types) for v in value])):
        return {
            't': 'MetaList',
            'c': [{'t': 'MetaString', 'c': str(v)} for v in value]
        }
    elif (isinstance(value, (tuple, list, set)) and
          all([isinstance(v, (float, int)) for v in value])):
        return {
            't': 'MetaList',
            'c': [{'t': 'MetaString', 'c': str(v)} for v in value]
        }
    else:
        raise NotImplementedError(
            "cannot construct meta element for : {}".format(value))


def sanitize_label(label):
    """from pandoc documentation
    The citation key must begin with a letter, digit, or _,
    and may contain alphanumerics, _,
    and internal punctuation characters (:.#$%&-+?<>~/)
    """
    label = str(label).lower()
    label = re.sub("[^a-zA-Z0-9-:\\.]+", "", label)
    # TODO raise warning if changed?
    return label


def elt(eltType, numargs):  # pylint: disable=invalid-name
    """Returns Element(``*value``) to create pandoc json elements.

    This should be used in place of pandocfilters.elt().  This version
    ensures that the content is stored in a list, not a tuple.
    """
    def element(*value):  # pylint: disable=invalid-name
        """Creates an element."""
        el = _elt(eltType, numargs)(*value)
        if isinstance(el['c'], tuple):
            el['c'] = list(el['c'])  # The content should be a list, not tuple
        return el
    element.__doc__ = "create an {}, require {} arguments".format(
        eltType, numargs)
    return element


class ElementTypes(object):
    """
    Improved version of pandocfilters element types
    """
    # Constructors for block elements

    Plain = elt('Plain', 1)
    Para = elt('Para', 1)
    CodeBlock = elt('CodeBlock', 2)
    RawBlock = elt('RawBlock', 2)
    BlockQuote = elt('BlockQuote', 1)
    OrderedList = elt('OrderedList', 2)
    BulletList = elt('BulletList', 1)
    DefinitionList = elt('DefinitionList', 1)
    Header = elt('Header', 3)
    HorizontalRule = elt('HorizontalRule', 0)
    Table = elt('Table', 5)
    AttrTable = elt('Table', 6)
    Div = elt('Div', 2)
    Null = elt('Null', 0)

    # Constructors for inline elements

    Str = elt('Str', 1)
    Emph = elt('Emph', 1)
    Strong = elt('Strong', 1)
    Strikeout = elt('Strikeout', 1)
    Superscript = elt('Superscript', 1)
    Subscript = elt('Subscript', 1)
    SmallCaps = elt('SmallCaps', 1)
    Quoted = elt('Quoted', 2)
    Cite = elt('Cite', 2)
    Code = elt('Code', 2)
    Space = elt('Space', 0)
    LineBreak = elt('LineBreak', 0)
    Math = elt('Math', 2)
    AttrMath = elt('Math', 3)
    RawInline = elt('RawInline', 2)
    Link = elt('Link', 3)
    Image = (elt('Image', 2) if compare_version('1.16', '<')
             else elt('Image', 3))
    Note = elt('Note', 1)
    SoftBreak = elt('SoftBreak', 0)
    Span = elt('Span', 2)

    # Constructors for meta objects
    MetaBool = elt('MetaBool', 1)
    MetaString = elt('MetaString', 1)
    # MetaMap
    # MetaInlines
    # MetaList
    # MetaBlocks


if __name__ == "__main__":
    _test_meta = {
        "jupyter": {
            "t": "MetaMap",
            "c": {
                "jupytext": {
                    "t": "MetaMap",
                    "c": {
                        "metadata_filter": {
                            "t": "MetaMap",
                            "c": {
                                "notebook": {
                                    "t": "MetaInlines",
                                    "c": [
                                        {
                                            "t": "Str",
                                            "c": "ipub"
                                        }
                                    ]
                                }
                            }
                        },
                        "text_representation": {
                            "t": "MetaMap",
                            "c": {
                                "format_version": {
                                    "t": "MetaInlines",
                                    "c": [
                                        {
                                            "t": "Str",
                                            "c": "1.0"
                                        }
                                    ]
                                },
                                "jupytext_version": {
                                    "t": "MetaInlines",
                                    "c": [
                                        {
                                            "t": "Str",
                                            "c": "0.8.6"
                                        }
                                    ]
                                },
                                "extension": {
                                    "t": "MetaInlines",
                                    "c": [
                                        {
                                            "t": "Str",
                                            "c": ".Rmd"
                                        }
                                    ]
                                },
                                "format_name": {
                                    "t": "MetaInlines",
                                    "c": [
                                        {
                                            "t": "Str",
                                            "c": "rmarkdown"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                },
                "kernelspec": {
                    "t": "MetaMap",
                    "c": {
                        "display_name": {
                            "t": "MetaInlines",
                            "c": [
                                {
                                    "t": "Str",
                                    "c": "Python"
                                },
                                {
                                    "t": "Space"
                                },
                                {
                                    "t": "Str",
                                    "c": "3"
                                }
                            ]
                        },
                        "name": {
                            "t": "MetaInlines",
                            "c": [
                                {
                                    "t": "Str",
                                    "c": "python3"
                                }
                            ]
                        },
                        "language": {
                            "t": "MetaInlines",
                            "c": [
                                {
                                    "t": "Str",
                                    "c": "python"
                                }
                            ]
                        }
                    }
                }
            }
        },
        "ipub": {
            "t": "MetaMap",
            "c": {
                "at_notation": {
                    "t": "MetaBool",
                    "c": True
                },
                "test": {
                    't': 'MetaList',
                    'c': [
                        {'t': 'MetaString', 'c': '1'},
                        {'t': 'MetaString', 'c': '2'}]}
            }
        }
    }
