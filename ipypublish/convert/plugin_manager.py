from collections import OrderedDict
import os
import inspect
import glob
import json
import importlib
import logging

from six import string_types
from jinja2 import DictLoader

from ipypublish.utils import pathlib
from ipypublish import export_plugins
from ipypublish.scripts.create_template import create_template

_TEMPLATE_KEY = 'new_template'


def handle_error(msg, err_type, raise_msg=None, log_msg=None):
    """handle an error, by logging it, then raising"""
    if raise_msg is None:
        raise_msg = msg
    if log_msg is None:
        log_msg = msg

    logging.error(log_msg)
    raise err_type(raise_msg)


def get_module_path(module):
    """return a directory path to a module"""
    return pathlib.Path(os.path.dirname(
        os.path.abspath(inspect.getfile(module))))


def get_plugin_path(plugin_name, plugin_folder_paths=()):
    # type (string, Tuple[str]) -> Union[string, None]
    """we search for a plugin name, which matches the supplied plugin name
    """
    for name, jsonpath in iter_all_plugin_paths(plugin_folder_paths):
        if name == plugin_name:
            return pathlib.Path(jsonpath)
    return None


def iter_all_plugin_paths(plugin_folder_paths=(), regex="*.json"):
    """we iterate through all json files in the
    supplied plugin_folder_paths, and then in the `export_plugins` folder
    """
    for plugin_folder_path in plugin_folder_paths:
        for jsonpath in glob.glob(os.path.join(plugin_folder_path, regex)):
            name = os.path.splitext(os.path.basename(jsonpath))[0]
            yield name, pathlib.Path(jsonpath)

    module_path = get_module_path(export_plugins)
    for jsonpath in glob.glob(os.path.join(str(module_path), regex)):
        name = os.path.splitext(os.path.basename(jsonpath))[0]
        yield name, pathlib.Path(jsonpath)


def load_plugin(plugin_path):

    if isinstance(plugin_path, string_types):
        plugin_path = pathlib.Path(plugin_path)

    with plugin_path.open() as fobj:
        data = json.load(fobj)
    # TODO validate against schema
    return data


def iter_all_plugin_infos(plugin_folder_paths=(), regex="*.json"):

    for name, path in iter_all_plugin_paths(plugin_folder_paths, regex):
        data = load_plugin(path)

        yield dict([
            ("key", str(name)),
            ("class", data["exporter"]["class"]),
            ("path", str(path)),
            ("description", data["description"])
        ])


def create_exporter_cls(class_str):
    """dynamically load export class"""
    export_class_path = class_str.split(".")
    module_path = ".".join(export_class_path[0:-1])
    class_name = export_class_path[-1]
    try:
        export_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        handle_error(
            "module {} containing exporter class {} not found".format(
                module_path, class_name), ModuleNotFoundError)
    if hasattr(export_module, class_name):
        export_class = getattr(export_module, class_name)
    else:
        handle_error(
            "module {} does not contain class {}".format(
                module_path, class_name), ImportError)

    # if a template is used we need to override the default template
    class BespokeTemplateExporter(export_class):
        """override the default template"""
        template_file = _TEMPLATE_KEY
    return BespokeTemplateExporter  # type: nbconvert.


def get_plugin_extension(plugin_path):
    """return the file extension of the exporter class"""
    data = load_plugin(plugin_path)
    exporter_cls = create_exporter_cls(data["exporter"]["class"])
    return exporter_cls.file_extension


def read_json_from_module(module_path, file_name, jtype):

    try:
        outline_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        handle_error(
            "module {} containing {} {} not found".format(
                module_path, jtype, file_name), ModuleNotFoundError)
    outline_path = os.path.join(
        str(get_module_path(outline_module)), file_name)
    if not os.path.exists(outline_path):
        handle_error(
            "the {} does not exist: {}".format(jtype, outline_path),
            IOError)
    with open(outline_path) as fobj:
        try:
            data = json.load(fobj)
        except Exception as err:
            handle_error("failed to read {} ({}): {}".format(
                jtype, outline_path, err), IOError)
    return data


def str_to_jinja(template_str):
    return DictLoader({_TEMPLATE_KEY: template_str})


def load_template(template_dict):

    if template_dict is None:
        return None

    outline_schema = read_json_from_module(
        template_dict["outline"]["module"],
        template_dict["outline"]["file"], "template outline")
    segments = []
    for segment in template_dict["segments"]:
        segments.append(
            read_json_from_module(segment["module"], segment["file"],
                                  "template segment"))

    template_str = create_template(outline_schema, segments)

    return str_to_jinja(template_str)
