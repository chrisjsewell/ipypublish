""" a module to convert between the old (Python script) plugin format,
and the new (JSON) one
"""
from typing import Dict, Tuple  # noqa: F401
import ast
import json


def assess_syntax(path):

    with open(path) as file_obj:
        content = file_obj.read()

    syntax_tree = ast.parse(content)

    docstring = ""  # docstring = ast.get_docstring(syntaxTree)
    unknowns = []
    imported = {}
    assignments = {}
    for i, child in enumerate(ast.iter_child_nodes(syntax_tree)):
        if (i == 0
            and isinstance(child, ast.Expr)
                and isinstance(child.value, ast.Str)):
            docstring = child.value.s
        elif isinstance(child, ast.ImportFrom):
            module = child.module
            for n in child.names:
                import_pth = module + "." + n.name
                imported[n.name if n.asname is None else n.asname] = import_pth
        elif isinstance(child, ast.Assign):
            targets = child.targets
            if len(targets) > 1:
                raise IOError(
                    "cannot handle expansion assignments "
                    "(e.g. `a, b = [1, 2]`)")
            target = child.targets[0]  # type: ast.Name
            assignments[target.id] = child.value
        else:
            unknowns.append(child)

    if unknowns:
        print("Warning this script can only handle 'ImportFrom' and 'Assign' "
              "syntax, found additional items: {}".format(unknowns))

    return docstring, imported, assignments


def ast_to_json(item, imported, assignments):
    """recursively convert ast items to json friendly values"""
    value = None
    if item in ['True', 'False', 'None']:  # python 2.7
        value = {'True': True, 'False': False, 'None': None}[item]
    elif hasattr(ast, "NameConstant") and isinstance(item, ast.NameConstant):
        value = item.value
    elif isinstance(item, ast.Str):
        value = item.s
    elif isinstance(item, ast.Num):
        value = item.n
    elif isinstance(item, ast.Name):
        if item.id in imported:
            value = imported[item.id]
        elif item.id in assignments:
            value = ast_to_json(assignments[item.id], imported, assignments)
        elif item.id in ['True', 'False', 'None']:  # python 2.7
            value = {'True': True, 'False': False, 'None': None}[item.id]
        else:
            raise ValueError(
                "could not find assignment '{}' in config".format(item.id))
    elif isinstance(item, (ast.List, ast.Tuple, ast.Set)):
        value = [ast_to_json(i, imported, assignments) for i in item.elts]
    elif isinstance(item, ast.Dict):
        value = convert_dict(item, imported, assignments)
    else:
        raise ValueError("could not handle ast item: {}".format(item))

    return value


def convert_dict(dct, imported, assignments):
    # type: (ast.Dict, Dict[str, str], dict) -> dict
    """recurse through and replace keys"""
    out_dict = {}
    for key, val in zip(dct.keys, dct.values):
        if not isinstance(key, ast.Str):
            raise ValueError(
                "expected key to be a Str; {}".format(key))
        out_dict[key.s] = ast_to_json(val, imported, assignments)

    return out_dict


def convert_oformat(oformat):

    if oformat == "Notebook":
        outline = None  # TODO do notebooks need template (they have currently)
        exporter = 'nbconvert.exporters.NotebookExporter'
    elif oformat == "Latex":
        exporter = 'nbconvert.exporters.LatexExporter'
        outline = {
            "module": "ipypublish.templates.outline_schemas",
            "file": "latex_outline.latex.j2"
        }
    elif oformat == "HTML":
        exporter = 'nbconvert.exporters.HTMLExporter'
        outline = {
            "module": "ipypublish.templates.outline_schemas",
            "file": "html_outline.html.j2"
        }
    elif oformat == "Slides":
        exporter = 'nbconvert.exporters.SlidesExporter'
        outline = {
            "module": "ipypublish.templates.outline_schemas",
            "file": "html_outline.html.j2"
        }
    else:
        raise ValueError("expected oformat to be: "
                         "'Notebook', 'Latex', 'HTML' or 'Slides'")
    return exporter, outline


def convert_config(config, exporter_class, allow_other):
    # type: (dict, str) -> dict
    """convert config into required exporter format"""
    filters = {}
    preprocs = {}
    other = {}
    # first parse
    for key, val in config.items():
        # TODO Exporter.filters and TemplateExporter.filters always the same?
        if key in ["Exporter.filters", "TemplateExporter.filters"]:
            filters.update(config[key])
        if key in ["Exporter.preprocessors", "TemplateExporter.preprocessors"]:
            if preprocs:
                raise ValueError(
                    "'config' contains both Exporter.preprocessors and "
                    "TemplateExporter.preprocessors")
            for p in val:
                pname = p.split(".")[-1]
                preprocs[pname] = {"class": p, "args": {}}
                # TODO move these special cases to seperate input/function
                if pname in ["LatexDocLinks", "LatexDocHTML"]:
                    preprocs[pname]["args"]["metapath"] = "${meta_path}"
                    preprocs[pname]["args"]["filesfolder"] = "${files_path}"

    # second parse
    for key, val in config.items():
        if key in ["Exporter.filters", "TemplateExporter.filters",
                   "Exporter.preprocessors", "TemplateExporter.preprocessors"]:
            continue
        if key.split(".")[0] in preprocs:
            preprocs[key.split(".")[0]]["args"][".".join(
                key.split(".")[1:])] = val
        else:
            other[key] = val

    if other and not allow_other:
        print("Warning: ignoring other args: {}".format(other))
        other = {}

    output = {
        "class": exporter_class,
        "filters": filters,
        "preprocessors": list(preprocs.values()),
        "other_args": other
    }
    return output


def replace_template_path(path):
    """ replace original template path with new dict """
    segments = path.split(".")
    module = ".".join(segments[0:-1])
    name = segments[-1]
    if module == "ipypublish.html.ipypublish":
        return {
            "module": "ipypublish.templates.segments",
            "file": "ipy-{0}.html-tplx.json".format(name)
        }
    elif module == "ipypublish.html.standard":
        return {
            "module": "ipypublish.templates.segments",
            "file": "std-{0}.html-tplx.json".format(name)
        }
    elif module == "ipypublish.latex.standard":
        return {
            "module": "ipypublish.templates.segments",
            "file": "std-{0}.latex-tpl.json".format(name)
        }
    elif module == "ipypublish.latex.ipypublish":
        return {
            "module": "ipypublish.templates.segments",
            "file": "ipy-{0}.latex-tpl.json".format(name)
        }
    else:
        print("Warning: unknown template path: {}".format(path))
        return {
            "module": module,
            "file": "{0}.json".format(name)
        }


def create_json(docstring, imported, assignments, allow_other=True):
    #  type: (str, Dict[str, str], dict, bool) -> dict
    """Set docstring here.

    Parameters
    ----------
    docstring: str
        the doc string of the module
    imported: dict
        imported classes
    assignments: dict
        assigned values (i.e. 'a = b')
    allow_other: bool
        whether to allow arguments in config,
        which do not relate to preprocessors

    Returns
    -------

    """

    oformat = None
    config = None
    template = None
    for value, expr in assignments.items():
        if value == 'oformat':
            if not isinstance(expr, ast.Str):
                raise ValueError(
                    "expected 'oformat' to be a Str; {}".format(expr))
            oformat = expr.s
        elif value == "config":
            if not isinstance(expr, ast.Dict):
                raise ValueError(
                    "expected 'config' to be a Dict; {}".format(expr))
            config = convert_dict(expr, imported, assignments)
        elif value == "template":
            if not isinstance(expr, ast.Call):
                raise ValueError(
                    "expected 'config' to be a call to create_tpl(x)")
            # func = expr.func  # TODO make sure func name is create_tpl/tplx
            args = expr.args
            keywords = expr.keywords
            if len(args) != 1 or len(keywords) > 0:
                raise ValueError("expected create_tpl(x) to have one argument")
            seg_list = args[0]
            if isinstance(seg_list, ast.ListComp):
                seg_list = seg_list.generators[0].iter
            if not isinstance(seg_list, ast.List):
                raise ValueError(
                    "expected create_tpl(x) arg to be a List; {}".format(
                        seg_list))
            segments = []
            for seg in seg_list.elts:
                if isinstance(seg, ast.Attribute):
                    seg_name = seg.value.id
                elif isinstance(seg, ast.Name):
                    seg_name = seg.id
                else:
                    raise ValueError(
                        "expected seg in template to be an Attribute; " +
                        "{1}".format(seg))

                if seg_name not in imported:
                    raise ValueError("segment '{}' not found".format(seg_name))
                segments.append(imported[seg_name])
            template = segments

    if oformat is None:
        raise ValueError("could not find 'oformat' assignment")
    if config is None:
        raise ValueError("could not find 'config' assignment")
    if template is None:
        raise ValueError("could not find 'template' assignment")

    exporter_class, outline = convert_oformat(oformat)
    exporter = convert_config(config, exporter_class, allow_other)

    if any(["biblio_natbib" in s for s in template]):
        exporter["filters"]["strip_ext"] = (
            "ipypublish.filters.filters.strip_ext")

    return {
        "description": docstring.splitlines(),
        "exporter": exporter,
        "template": None if outline is None else {
            "outline": outline,
            "segments": [replace_template_path(s) for s in template]
        }
    }


def convert_to_json(path, outpath=None, ignore_other=False):
    """Set docstring here.

    Parameters
    ----------
    path: str
        input module path
    outpath=None: str or None
        if set, output json to this path
    ignore_other: bool
        whether to ignore arguments in config,
        which do not relate to preprocessors
    Returns
    -------

    """
    _docstring, _imported, _assignments = assess_syntax(path)
    # print(_docstring)
    # print()
    # print(_imported)
    # print()
    # print(_assignments)
    output = create_json(_docstring, _imported, _assignments, not ignore_other)
    if outpath:
        with open(outpath, "w") as file_obj:
            json.dump(output, file_obj, indent=2)
    return json.dumps(output, indent=2)


if __name__ == "__main__":

    if False:
        import glob
        import os
        for path in glob.glob(
                "/Users/cjs14/GitHub/ipypublish"
                "/ipypublish/export_plugins/*.py"):
            dirname = os.path.dirname(path)
            name = os.path.splitext(os.path.basename(path))[0]
            try:
                convert_to_json(path, os.path.join(dirname, name + ".json"),
                                ignore_other=True)
            except ValueError as err:
                print("{0} failed: {1}".format(path, err))

    convert_to_json(
        "/Users/cjs14/GitHub/ipypublish"
        "/ipypublish_plugins/example_new_plugin.py",
        "/Users/cjs14/GitHub/ipypublish"
        "/ipypublish_plugins/example_new_plugin.json")
