from collections import deque
import io
import logging

logger = logging.getLogger(__name__)


def import_texsoup():
    try:
        from TexSoup import TexSoup
        from TexSoup.utils import TokenWithPosition
        from TexSoup.data import RArg, OArg
    except ImportError:
        raise ImportError(
            "to parse tex files, TexSoup must be installed: \n"
            "pip install texsoup\n"
            "conda install -c conda-forge texsoup")
    except SyntaxError:
        raise ImportError('TexSoup package is broken on python 2.7, '
                          'so can not be imported for tex parsing')
    return {
        "TexSoup": TexSoup,
        "RArg": RArg,
        "OArg": OArg,
        "TokenWithPosition": TokenWithPosition
    }


def _create_msg_error(msg, node=None, row=None):
    """create error message, optionally including TexNode and row"""
    text = msg.strip()
    if row is not None:
        text = "(row {}) ".format(row) + text
    if hasattr(node, "name"):
        text = text + ": {}".format(node.name)
    return text


def extract_required_val(rarg):
    """extract the value of a TexSoup RArg"""
    RArg = import_texsoup()["RArg"]
    if not isinstance(rarg, RArg):
        raise ValueError(
            "expected {} to be a required argument".format(type(rarg)))
    return rarg.value


def _extract_parameters(texsoup_exprs):
    """extract the parameters from a TexSoup expression list"""
    RArg = import_texsoup()["RArg"]
    TokenWithPosition = import_texsoup()["TokenWithPosition"]
    expressions = deque(texsoup_exprs)
    param_name = None
    params = {}
    errors = []
    while expressions:
        expr = expressions.popleft()
        if isinstance(expr, TokenWithPosition):
            # TODO is this the best way to extract parameter name?
            param_name = expr.text.replace(",", "").replace("=", "").strip()
        elif isinstance(expr, RArg):
            if param_name is None:
                errors.append(
                    "expected expression "
                    "'{}' to precede a parameter name".format(expr))
                break
            if param_name in params:
                errors.append(
                    "parameter '{}' already defined".format(param_name))
            else:
                params[param_name] = expr.value
            param_name = None
        else:
            errors.append(
                "expected expression '{}' ".format(expr) +
                "to be a parameter name or required argument")
            break

    if param_name is not None:
        pass  # allowed since last expr may be new line
        # errors.append(
        #     "parameter '{}' is not assigned a value".format(param_name))

    return params, errors


def extract_parameters(argument):
    """extract parameters from a TexSoup OArg or Arg"""
    RArg = import_texsoup()["RArg"]
    OArg = import_texsoup()["OArg"]
    if not isinstance(argument, (OArg, RArg)):
        raise ValueError(
            "expected {} to be of type OArg or RArg".format(type(argument)))

    opt_params, errors = _extract_parameters(argument.exprs)

    return opt_params, errors


def create_newgloss_dict(gterm, row=None):
    """
    """
    arguments = list(gterm.args)
    fields = {}

    if len(arguments) != 2:
        msg = _create_msg_error(
            "could not parse newglossaryterm (arguments != 2)", gterm, row)
        raise IOError(msg)

    key = extract_required_val(arguments[0])

    params, errors = extract_parameters(arguments[1])

    for error in errors:
        msg = _create_msg_error(
            "error reading 'parameter' block: {}".format(error),
            gterm, row)
        raise IOError(msg)

    for param_name, param_value in params.items():

        if param_name in fields:
            raise IOError(
                "duplicate parameter '{0}' in key '{1}'".format(
                    param_name, key))

        fields[param_name] = param_value

    return key, fields


def create_newacronym_dict(acronym, row=None):
    """
    """
    OArg = import_texsoup()["OArg"]

    arguments = list(acronym.args)
    fields = {}

    if len(arguments) < 3:
        msg = _create_msg_error(
            "could not parse newacronym (too few arguments)", acronym, row)
        raise IOError(msg)
    if len(arguments) > 4:
        msg = _create_msg_error(
            "could not parse newacronym (too many arguments)", acronym, row)
        raise IOError(msg)

    key = extract_required_val(arguments[-3])
    abbreviation = extract_required_val(arguments[-2])
    name = extract_required_val(arguments[-1])

    if len(arguments) == 4:
        options = arguments[0]

        if not isinstance(options, OArg):
            msg = _create_msg_error(
                "expected first argument of newacronym to be 'optional",
                acronym, row)
            raise IOError(msg)

        opt_params, errors = extract_parameters(options)

        for error in errors:
            msg = _create_msg_error(
                "error reading newacronym 'optional' block: {}".format(error),
                acronym, row)
            raise IOError(msg)

        for opt_name, opt_value in opt_params.items():
            if opt_name in fields:
                raise IOError(
                    "duplicate parameter '{0}' in key '{1}'".format(
                        opt_name, key))
            fields[opt_name] = opt_value

    return key, abbreviation, name, fields


def parse_tex(text_str=None, path=None, encoding='utf8',
              abbrev_field="abbreviation", fname_field="longname",
              skip_ioerrors=False):
    """parse a tex file containing newglossaryentry and/or newacronym to dict

    Parameters
    ----------
    text_str=None: str
        string representing the tex file
    path=None: str
        path to the tex file
    encoding='utf8': str
        tex file encoding
    abbrev_field="abbreviation": str
        field key for acronym abbreviation
    fname_field="longname": str
        field key for acronym full name
    skip_ioerrors=False: bool
        skip errors on reading a single entry

    Returns
    -------
    dict: glossaryterms
        {key: fields}
    dict: acronyms
        {key: fields}

    """
    TexSoup = import_texsoup()["TexSoup"]

    if sum([e is not None for e in [text_str, path]]) != 1:
        raise ValueError("only one of text_str or path must be supplied")
    elif path is not None:
        if text_str is not None:
            raise ValueError(
                'text_str and path cannot be set at the same time')
        with io.open(path, encoding=encoding) as fobj:
            text_str = fobj.read()

    latex_tree = TexSoup(text_str)

    keys = []
    gterms = {}
    acronyms = {}

    for gterm in latex_tree.find_all("newglossaryentry"):
        try:
            key, fields = create_newgloss_dict(gterm)
        except IOError:
            if skip_ioerrors:
                continue
            raise
        if key in keys:
            raise KeyError("duplicate key: {}".format(key))
        keys.append(key)
        gterms[key] = fields

    for acronym in latex_tree.find_all("newacronym"):
        try:
            key, abbreviation, name, fields = create_newacronym_dict(acronym)
        except IOError:
            if skip_ioerrors:
                continue
            raise
        if key in keys:
            raise KeyError("duplicate key: {}".format(key))
        keys.append(key)
        fields[abbrev_field] = abbreviation
        fields[fname_field] = name
        acronyms[key] = fields

    return gterms, acronyms
