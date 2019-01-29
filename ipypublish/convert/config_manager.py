import os
import inspect
import glob
import json
import importlib
import logging

from six import string_types
from jinja2 import DictLoader
import jsonschema

from ipypublish.utils import pathlib
from ipypublish import export_plugins
from ipypublish.scripts.create_template import create_template

_TEMPLATE_KEY = 'new_template'
_EXPORT_SCHEMA_FILE = "export_config.schema.json"
_EXPORT_SCHEMA = None


def handle_error(msg, err_type, raise_msg=None, log_msg=None):
    """handle an error, by logging it, then raising"""
    if raise_msg is None:
        raise_msg = msg
    if log_msg is None:
        log_msg = msg

    logging.error(log_msg)
    raise err_type(raise_msg)


def read_json_from_directory(dir_path, file_name, jtype):
    """load a json file situated in a directory"""
    if isinstance(dir_path, string_types):
        dir_path = pathlib.Path(dir_path)

    file_path = dir_path.joinpath(file_name)

    if not file_path.exists():
        handle_error(
            "the {} does not exist: {}".format(jtype, file_path),
            IOError)

    with file_path.open() as fobj:
        try:
            data = json.load(fobj)
        except Exception as err:
            handle_error("failed to read {} ({}): {}".format(
                jtype, file_path, err), IOError)
    return data


def get_module_path(module):
    """return a directory path to a module"""
    return pathlib.Path(os.path.dirname(
        os.path.abspath(inspect.getfile(module))))


def read_json_from_module(module_path, file_name, jtype):
    """load a json file situated in a python module"""
    try:
        outline_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        handle_error(
            "module {} containing {} {} not found".format(
                module_path, jtype, file_name), ModuleNotFoundError)

    return read_json_from_directory(get_module_path(outline_module),
                                    file_name, jtype)


def get_export_config_path(export_key, config_folder_paths=()):
    # type (string, Tuple[str]) -> Union[string, None]
    """we search for a plugin name, which matches the supplied plugin name
    """
    for name, jsonpath in iter_all_export_paths(config_folder_paths):
        if name == export_key:
            return pathlib.Path(jsonpath)
    return None


def iter_all_export_paths(config_folder_paths=(), regex="*.json"):
    """we iterate through all json files in the
    supplied plugin_folder_paths, and then in the `export_plugins` folder
    """
    for plugin_folder_path in config_folder_paths:
        for jsonpath in glob.glob(os.path.join(plugin_folder_path, regex)):
            name = os.path.splitext(os.path.basename(jsonpath))[0]
            yield name, pathlib.Path(jsonpath)

    module_path = get_module_path(export_plugins)
    for jsonpath in glob.glob(os.path.join(str(module_path), regex)):
        name = os.path.splitext(os.path.basename(jsonpath))[0]
        yield name, pathlib.Path(jsonpath)


def load_export_config(export_config_path):
    """load the export configuration"""
    if isinstance(export_config_path, string_types):
        export_config_path = pathlib.Path(export_config_path)

    data = read_json_from_directory(
        export_config_path.parent, export_config_path.name,
        "export configuration")

    # validate against schema
    global _EXPORT_SCHEMA
    if _EXPORT_SCHEMA is None:
        # lazy load schema once
        _EXPORT_SCHEMA = read_json_from_directory(
            os.path.dirname(os.path.realpath(__file__)), _EXPORT_SCHEMA_FILE,
            "export configuration schema")
    try:
        jsonschema.validate(data, _EXPORT_SCHEMA)
    except jsonschema.ValidationError as err:
        handle_error(
            "validation of export config {} failed against {}: {}".format(
                export_config_path, _EXPORT_SCHEMA_FILE, err.message),
            jsonschema.ValidationError)

    return data


def iter_all_export_infos(config_folder_paths=(), regex="*.json"):
    """iterate through all export configuration and yield a dict of info"""
    for name, path in iter_all_export_paths(config_folder_paths, regex):
        data = load_export_config(path)

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


def get_export_extension(export_config_path):
    """return the file extension of the exporter class"""
    data = load_export_config(export_config_path)
    exporter_cls = create_exporter_cls(data["exporter"]["class"])
    return exporter_cls.file_extension


def str_to_jinja(template_str):
    return DictLoader({_TEMPLATE_KEY: template_str})


def load_template(template_dict):

    if template_dict is None:
        return None

    if "directory" in template_dict["outline"]:
        outline_schema = read_json_from_directory(
            template_dict["outline"]["directory"],
            template_dict["outline"]["file"], "template outline")
    else:
        outline_schema = read_json_from_module(
            template_dict["outline"]["module"],
            template_dict["outline"]["file"], "template outline")
    segments = []
    for segment in template_dict["segments"]:

        if "directory" in segment:
            seg_data = read_json_from_directory(
                segment["directory"],
                segment["file"], "template segment")
        else:
            seg_data = read_json_from_module(
                segment["module"],
                segment["file"], "template segment")

        segments.append(seg_data)

    template_str = create_template(outline_schema, segments)

    return str_to_jinja(template_str)
