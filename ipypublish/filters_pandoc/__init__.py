"""
pandoc filters for the ipypublish format
"""
# import sys
from six import string_types
import panflute as pf
pf.elements.RAW_FORMATS.add("latex")
pf.elements.RAW_FORMATS.add("tex")
pf.elements.RAW_FORMATS.add("rst")
pf.elements.RAW_FORMATS.add("html5")


# see https://github.com/sergiocorreia/panflute/issues/97
# TODO delete this when fixed
# if sys.version_info[0] == 2 or True:
def builtin2meta(val):
    if isinstance(val, bool):
        return pf.MetaBool(val)
    elif isinstance(val, (float, int)):
        return pf.MetaString(str(val))
    elif isinstance(val, string_types):
        return pf.MetaString(val)
    elif isinstance(val, list):
        return pf.MetaList(*[builtin2meta(x) for x in val])
    elif isinstance(val, dict):
        return pf.MetaMap(*[(k, builtin2meta(v)) for k, v in val.items()])
    elif isinstance(val, pf.Block):
        return pf.MetaBlocks(val)
    elif isinstance(val, pf.Inline):
        return pf.MetaInlines(val)
    elif isinstance(val, (pf.MetaBool, pf.MetaString, pf.MetaValue,
                          pf.MetaList, pf.MetaMap, pf.MetaBlocks,
                          pf.MetaInlines)):
        return val

    raise TypeError("unknown type: {} (type: {})".format(val, type(val)))


pf.elements.builtin2meta = builtin2meta
