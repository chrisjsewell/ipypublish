from collections import OrderedDict
import copy
import io
import json
import re

from six import string_types
from nbconvert.utils.pandoc import get_pandoc_version
from distutils.version import LooseVersion
import panflute as pf

from panflute import Element, Doc  # noqa: F401
from types import FunctionType  # noqa: F401

from ipypublish.filters_pandoc.definitions import IPUB_META_ROUTE


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
        doc = pf.convert_text(
            in_str, input_format=in_format, standalone=True)
        # f = io.StringIO(in_json)
        # doc = pf.load(f)
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
    # with io.StringIO() as f:
    #     pf.dump(doc, f)
    #     jsonstr = f.getvalue()
    # jsonstr = json.dumps(out_doc.to_json()
    out_str = pf.convert_text(out_doc,
                              input_format="panflute",
                              output_format=out_format)

    # post-process final str
    if strip_blank_lines:
        out_str = out_str.replace("\n\n", "\n")

    return out_str


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


def strip_quotes(string):
    # type: (str) -> str
    if string.startswith("'") and string.endswith("'"):
        string = string[1:-1]
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string


def find_attributes(element, allow_space=True,
                    search_left=False, include_element=False):
    """find an attribute 'container' for an element,
    of the form <element><space>{#id .class1 .class2 a=1 b="a string"}
    and extract its content

    Parameters
    ----------
    element:
        the element to find attributes for
    allow_space=True: bool
        whether to allow space between the element and attribute container
    search_left=False: bool
        search to the left of the element, rather than the right
    include_element=False: bool
        whether to include the element in the search


    Returns
    -------
    dict or None:
        {"classes": list[str], "attributes": dict[str],
         "id": str, "elements": list[Element]}, where elements is
         the elements containing the attributes (including space)

    """
    if search_left:
        return _search_attribute_left(element, include_element, allow_space)
    else:
        return _search_attribute_right(element, include_element, allow_space)


def _search_attribute_right(element, include_element, allow_space):
    if (not element.next) and not include_element:
        return None

    if include_element:
        adjacent = element
    else:
        adjacent = element.next

    attr_elements = []
    found_start = False
    found_end = False
    while adjacent:
        if (isinstance(adjacent, pf.Space) and allow_space):
            attr_elements.append(adjacent)
            adjacent = adjacent.next
            continue
        elif (isinstance(adjacent, pf.Str)
              #   and adjacent.text.startswith("{")
              #   and adjacent.text.endswith("}")):
              and re.search(r'^\{[^}]*\}', adjacent.text)):
            # TODO this won't handle } in strings, e.g. {a="} "}
            found_start = True
            found_end = True
            attr_elements.append(adjacent)
            break
        elif (isinstance(adjacent, pf.Str)
              #   and adjacent.text.startswith("{")):
              and re.search(r'^[^\}]*\{', adjacent.text)):
            found_start = True
            found_end = False
            attr_elements.append(adjacent)
            break
        break
        # adjacent = adjacent.next

    if found_start and not found_end:
        adjacent = adjacent.next
        while adjacent:
            if (isinstance(adjacent, pf.Str)
                    # and adjacent.text.endswith("}")):
                    and re.search(r'^[^\{]*\}', adjacent.text)):
                # TODO this won't handle } in strings, e.g. {a="} "}
                found_end = True
                attr_elements.append(adjacent)
                break
            else:
                attr_elements.append(adjacent)
            adjacent = adjacent.next

    if not (found_start and found_end):
        return None

    attribute_str = pf.stringify(
        pf.Para(*attr_elements)).replace("\n", " ").strip()

    # split into the label and the rest
    match = re.match(r"^\{(#[^\s]+|)([^\}]*)\}", attribute_str)
    if not match:
        raise ValueError(attribute_str)
    classes, attributes = process_attributes(match.group(2))

    new_str = attribute_str[len(match.group(0)):]

    return {
        "id": match.group(1)[1:],
        "classes": classes,
        "attributes": attributes,
        "elements": attr_elements,
        "append": pf.Str(new_str) if new_str else None
    }


def _search_attribute_left(element, include_element, allow_space):
    if (not element.prev) and not include_element:
        return None

    if include_element:
        adjacent = element
    else:
        adjacent = element.prev

    attr_elements = []
    found_start = False
    found_end = False
    while adjacent:
        if (isinstance(adjacent, pf.Space) and allow_space):
            attr_elements.append(adjacent)
            adjacent = adjacent.prev
            continue
        elif (isinstance(adjacent, pf.Str)
              and adjacent.text.endswith("}")
              and adjacent.text.startswith("{")):
            # TODO this won't handle } in strings, e.g. {a="} "}
            # TODO this won't handle characters after } e.g. {a=1})
            found_start = True
            found_end = True
            attr_elements.append(adjacent)
            break
        elif (isinstance(adjacent, pf.Str)
              and adjacent.text.endswith("}")):
            found_start = False
            found_end = True
            attr_elements.append(adjacent)
            break
        break
        # adjacent = adjacent.prev

    if found_end and not found_start:
        adjacent = adjacent.prev
        while adjacent:
            if (isinstance(adjacent, pf.Str)
                    and adjacent.text.startswith("{")):
                # TODO this won't handle { in strings, e.g. {a="{ "}
                # TODO this won't handle characters before { e.g. ({a=1}
                found_start = True
                attr_elements.append(adjacent)
                break
            else:
                attr_elements.append(adjacent)
            adjacent = adjacent.prev

    if not (found_start and found_end):
        return None

    attr_elements = list(reversed(attr_elements))

    attribute_str = pf.stringify(
        pf.Para(*attr_elements)).replace("\n", " ").strip()

    # split into the label and the rest
    match = re.match("^\\{(#[^\\s]+|)([^\\}]*)\\}$", attribute_str)
    if not match:
        raise ValueError(attribute_str)
    classes, attributes = process_attributes(match.group(2))

    return {
        "id": match.group(1)[1:],
        "classes": classes,
        "attributes": attributes,
        "elements": attr_elements,
        "append": None
    }


def process_attributes(attr_string):
    """process a string of classes and attributes,
    e.g. '.class-name .other a=1 b="some text"' will be returned as:
    ["class-name", "other"], {"a": 1, "b": "some text"}

    Returns:
    list: classes
    dict: attributes
    """
    # find classes, denoted by .class-name
    classes = [c[1][1:] for c in re.findall('(^|\\s)(\\.[\\-\\_a-zA-Z]+)',
                                            attr_string)]
    # find attributes, denoted by a=b, respecting quotes
    attr = {c[1]: strip_quotes(c[2]) for c in re.findall(
        '(^|\\s)([\\-\\_a-zA-Z]+)\\s*=\\s*(\\".+\\"|\\\'.+\\\'|[^\\s\\"\\\']+)',  # noqa: E501
        attr_string)}
    # TODO this generally works, but should be stricter against any weird
    # fringe cases

    # TODO add tests
    return classes, attr


def convert_attributes(attr):
    """attempt to convert values to python types, e.g. float, list, dict"""
    attr = copy.deepcopy(attr)
    for key in list(attr.keys()):
        try:
            new_value = json.loads(attr[key])
            attr[key] = new_value
        except Exception:
            pass
    return attr


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


def get_option(locations, keypath, default=None,
               delimiter=".", error_on_missing=False):
    """ fetch an option variable from a hierarchy of preferred locations

    The value returned will be from the first available location or the default

    Parameters
    ----------
    locations: list[dict]
        a list of mappings to search in
    keypath: list[str] or str
        a key path to search in, if str, then split by delimiter
    default=None: object
        a default value to return
    delimiter: str
        if a str then the keypath is expected to be a str
    error_on_missing: bool
        raise KeyError if not found in any of the options

    Examples
    --------

    >>> a = {"m": 1}
    >>> b = {"x": {"y": 2}}
    >>> c = {"x": {"y": 3}}
    >>> get_option([a, b, c], keypath=("x", "y"))
    2
    >>> get_option([a, c, b], keypath=("x", "y"))
    3
    >>> get_option([a, c, b], keypath="x.y")
    3
    >>> get_option([a, c, b], keypath="l", default=4)
    4

    """
    if isinstance(keypath, string_types):
        keypath = keypath.split(delimiter)

    found_var = False
    variable = None

    for opt in locations:
        final_opt = opt
        found_key = True
        for key in keypath:
            try:
                final_opt = final_opt[key]
            except (KeyError, TypeError):
                found_key = False
                break
        if found_key:
            found_var = True
            variable = final_opt
            break

    if found_var:
        return variable
    elif error_on_missing:
        raise ValueError(
            "could not retrieve the option keypath: {}".format(keypath))

    return default


def create_ipub_meta(options):
    meta = {}
    submeta = meta
    for key in IPUB_META_ROUTE.split(".")[:-1]:
        submeta[key] = {}
        submeta = submeta[key]
    submeta[IPUB_META_ROUTE.split(".")[-1]] = options
    return meta


def get_panflute_containers(element):
    """return list of all possible container classes for an element"""
    panflute_inline_containers = (
        pf.Cite,
        pf.Emph,
        pf.Header,
        pf.Image,
        pf.LineItem,
        pf.Link,
        pf.Para,
        pf.Plain,
        pf.Quoted,
        pf.SmallCaps,
        pf.Span,
        pf.Strikeout,
        pf.Strong,
        pf.Subscript,
        pf.Superscript
    )

    panflute_block_containers = (
        pf.BlockQuote,
        pf.Definition,
        pf.Div,
        pf.Doc,
        pf.ListItem,
        pf.Note,
        pf.TableCell
    )

    if issubclass(element, pf.Inline):
        return panflute_inline_containers

    elif issubclass(element, pf.Block):
        return panflute_block_containers

    raise TypeError("not Inline or Block: {}".format(element))


def get_pf_content_attr(container, target):

    panflute_inline_containers = [
        pf.Cite,
        pf.Emph,
        pf.Header,
        pf.Image,
        pf.LineItem,
        pf.Link,
        pf.Para,
        pf.Plain,
        pf.Quoted,
        pf.SmallCaps,
        pf.Span,
        pf.Strikeout,
        pf.Strong,
        pf.Subscript,
        pf.Superscript,
        pf.Table,
        pf.DefinitionItem
    ]

    panflute_block_containers = (
        pf.BlockQuote,
        pf.Definition,
        pf.Div,
        pf.Doc,
        pf.ListItem,
        pf.Note,
        pf.TableCell
    )

    if issubclass(target, pf.Cite):
        # we assume a Cite can't contain another Cite
        if not isinstance(container, tuple(panflute_inline_containers[1:])):
            return False

    if issubclass(target, pf.Inline):
        if isinstance(container, tuple(panflute_inline_containers)):
            if isinstance(container, pf.Table):
                return "caption"
            elif isinstance(container, pf.DefinitionItem):
                return "term"
            else:
                return "content"
        else:
            return False

    if issubclass(target, pf.Block):
        if isinstance(container, tuple(panflute_block_containers)):
            return "content"
        else:
            return False

    raise TypeError("target not Inline or Block: {}".format(target))
