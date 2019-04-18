""" a module to convert between the old (Python script) segment format,
and the new (JSON) one
"""
from typing import Dict, Tuple  # noqa: F401
import os
import ast
import json


def assess_syntax(path):

    with open(path) as file_obj:
        content = file_obj.read()

    syntax_tree = ast.parse(content)

    docstring = ""  # docstring = ast.get_docstring(syntaxTree)
    dct = None
    dtype = None
    for i, child in enumerate(ast.iter_child_nodes(syntax_tree)):
        if (i == 0
            and isinstance(child, ast.Expr)
                and isinstance(child.value, ast.Str)):
            docstring = child.value.s
        elif isinstance(child, ast.Assign):
            targets = child.targets
            if len(targets) > 1:
                continue
            target = child.targets[0]  # type: ast.Name
            dtype = target.id
            if dtype not in ["tpl_dict", "tplx_dict"]:
                continue
            if not isinstance(child.value, ast.Dict):
                raise ValueError(
                    "expected {} to be of type Dict: {}".format(
                        dtype, child.value))
            dct = child.value
            break

    if dct is None:
        raise IOError("could not find tpl(x)_dict")

    output = {}
    for key, value in zip(dct.keys, dct.values):
        if not isinstance(key, ast.Str):
            raise ValueError(
                    "expected {} key to be of type Str: {}".format(
                        dtype, key))
        if not isinstance(value, ast.Str):
            raise ValueError(
                    "expected {} value be of type Str: {}".format(
                        dtype, value))
        output[key.s] = value.s

    return {
        "identifier": os.path.splitext(os.path.basename(path))[0],
        "description": docstring,
        "segments": output,
        "$schema": "../../schema/segment.schema.json"
     }


def py_to_json(path, outpath=None):
    output = assess_syntax(path)
    if outpath:
        with open(outpath, "w") as file_obj:
            json.dump(output, file_obj, indent=2)
    return json.dumps(output, indent=2)


if __name__ == "__main__":
    import glob

    _dir_path = os.path.dirname(os.path.realpath(__file__))
    _ext = ".tpl.json"

    for _path in glob.glob(os.path.join(_dir_path, "**", "*.py")):

        _name = os.path.splitext(os.path.basename(_path))[0]
        _folder = os.path.basename(os.path.dirname(_path))
        if _folder == "ipypublish":
            _prefix = "ipy-"
        else:
            _prefix = "std-"

        _outpath = os.path.join(os.path.dirname(_path), _prefix+_name+_ext)

        py_to_json(_path, _outpath)
