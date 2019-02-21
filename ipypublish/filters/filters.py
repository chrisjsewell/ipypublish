from collections import OrderedDict
import re
import os
from six import string_types


def strip_ext(path):
    return os.path.splitext(path)[0]


def basename(path, ext=False):
    basename = os.path.basename(path)
    if not ext:
        basename = os.path.splitext(basename)[0]
    return basename


def get_empty_lines(text):
    """Get number of empty lines before and after text."""
    before = len(text) - len(text.lstrip('\n'))
    after = len(text) - len(text.strip('\n')) - before
    return before, after


def wrap_latex(input, max_length=75, **kwargs):
    if len(input) > max_length:
        # remove double dollars, as they don't allow word wrap
        if len(input) > 3:
            if input[0:2] == '$$' and input[-2:] == '$$':
                input = input[1:-1]
        # change \left( and \right) to \bigg( and \bigg), as allow word wrap
        input = input.replace(r'\left(', r'\big(')
        input = input.replace(r'\right)', r'\big)')

    return input


def remove_dollars(text):
    """remove dollars from start/end of text"""
    while text.startswith('$'):
        text = text[1:]
    while text.endswith('$'):
        text = text[0:-1]
    return text


def wrap_eqn(text, cell_meta, nb_meta, out="latex"):
    """ wrap an equation in a latex equation environment

    environment obtained (if present) from cell_meta.ipub.equation.environment)
    label obtained (if present) from cell_meta.ipub.equation.label)
    also, nb_meta.ipub.enable_breqn used

    Parameters
    ----------
    text: str
    cell_meta: dict
        the cell metadata
    nb_meta: dict
        the notebook metadata

    Returns
    -------
    new_text: str

    """
    numbered = True
    try:
        environment = cell_meta["ipub"]["equation"]["environment"]
    except (KeyError, TypeError):
        environment = None
    if environment == "none":
        environment = None
    elif environment in ["equation*", "align*", "multline*",
                         "gather*", "eqnarray*"]:
        numbered = False
    elif environment in ["equation", "align",
                         "multline", "gather", "eqnarray"]:
        pass
    elif environment == "breqn" and out == "latex":
        if nb_meta.get("ipub", {}).get("enable_breqn", False):
            environment = "dmath*"
        else:
            environment = None
    else:
        environment = None

    try:
        label = cell_meta["ipub"]["equation"]["label"]
    except (KeyError, TypeError):
        label = None

    if environment:
        outtext = "\\begin{{{0}}}".format(environment)
        if label and numbered and out == "latex":
            outtext += "\\label{{{0}}}".format(label)
        outtext += "\n" + remove_dollars(text)
        outtext += "\n\\end{{{0}}}".format(environment)
    else:
        outtext = text

    return outtext


def get_caption(etype, cell_meta, resources):
    """return an ipypublish caption or False

    captions can either be located at cell_meta.ipub.<type>.caption,
    or at resources.caption[cell_meta.ipub.<type>.label]

    the resources version is proritised
    """
    try:
        caption = cell_meta["ipub"][etype]["caption"]
    except (KeyError, TypeError):
        caption = False

    try:
        label = cell_meta["ipub"][etype]["label"]
    except (KeyError, TypeError):
        label = False

    rcaption = False
    if label:
        try:
            rcaption = resources["caption"][label]
        except (KeyError, TypeError):
            pass

    if rcaption:
        return rcaption
    return caption


def first_para(input, **kwargs):
    r"""get only ttext before a \n (i.e. the fist paragraph)"""
    return input.split('\n')[0]


def _write_roman(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num > 0:
                roman_num(num)
            else:
                break

    return "".join([a for a in roman_num(num)])


def _repl(match):
    return _write_roman(int(match.group(0)))


def create_key(input, **kwargs):
    """create sanitized key string which only contains lowercase letters,
    (semi)colons as c, underscores as u and numbers as roman numerals
    in this way the keys with different input should mainly be unique

    >>> create_key('fig:A_10name56')
    'figcauxnamelvi'

    """
    input = re.compile(r"\d+").sub(_repl, input)
    input = input.replace(':', 'c')
    input = input.replace(';', 'c')
    input = input.replace('_', 'u')
    return re.sub('[^a-zA-Z]+', '', str(input)).lower()


def _split_option(item, original):
    opt = item.split("=")
    if len(opt) > 2:
        raise ValueError(
            "item '{}' from '{}' contains multiple '='".format(
                item, original))
    elif len(opt) == 1:
        return opt[0].strip(), None
    else:
        return [o.strip() for o in opt]


def dict_to_kwds(inobject, kwdstr='', overwrite=True):
    """ convert a dictionary to a string of keywords,
    or, if a list, a string of options

    append to an existing options string (without duplication)

    Parameters
    ----------
    dct : dict
    kwdstr: str
        initial keyword string
    overwrite: bool
        overwrite the option, if it already exists with a different value

    Examples
    --------
    >>> dict_to_kwds({"a":1,"c":3},'a=1,b=2')
    'a=1,b=2,c=3'
    >>> dict_to_kwds(['a', 'c'],'a,b')
    'a,b,c'

    """
    if not isinstance(kwdstr, string_types):
        raise ValueError("kwdstr '{}' not a string".format(kwdstr))

    optdict = {}
    for item in kwdstr.split(","):
        if item == "":
            continue
        ikey, ival = _split_option(item, kwdstr)
        if ikey in optdict:
            raise ValueError(
                "kwdstr '{}' contain multiple references to '{}'".format(
                    kwdstr, ikey
                ))
        optdict[ikey] = ival

    if isinstance(inobject, (list, tuple)):
        for item in inobject:
            if item == "":
                continue
            if not isinstance(item, string_types):
                raise ValueError(
                    "option '{}' from option list is not a string: {}".format(
                        item, kwdstr))
            okey, oval = _split_option(item, inobject)
            if okey not in optdict or overwrite:
                optdict[okey] = oval
    else:
        for kkey in sorted(inobject.keys()):
            keystr = str(kkey)
            if keystr not in optdict or overwrite:
                optdict[kkey] = str(inobject[kkey])

    outstring1 = []
    outstring2 = []
    for skey in sorted(optdict.keys()):
        if optdict[skey] is None:
            outstring1.append(skey)
        else:
            outstring2.append("{}={}".format(skey, optdict[skey]))

    outstring = outstring1 + outstring2
    return ",".join(outstring)


def is_equation(text):
    """test if a piece of text is a latex equation, by how it is wrapped"""
    text = text.strip()

    if any([text.startswith('\\begin{{{0}}}'.format(env))
            and text.endswith('\\end{{{0}}}'.format(env))
            for env in
            ['equation', 'split', 'equation*', 'align', 'align*',
             'multline', 'multline*', 'gather', 'gather*']]):
        return True
    elif text.startswith('$') and text.endswith('$'):
        return True
    else:
        return False


if __name__ == "__main__":

    print(dict_to_kwds(['a', 'c'], 'e,b,d=3'))
