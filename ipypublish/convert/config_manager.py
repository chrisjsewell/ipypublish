import os
import glob
import importlib
import logging

from six import string_types
from jinja2 import DictLoader
import jsonschema
import nbconvert  # noqa: F401

from ipypublish.utils import (pathlib, handle_error, get_module_path,
                              read_file_from_directory, read_file_from_module)
from ipypublish import export_plugins
from ipypublish import schema
from ipypublish.templates.create_template import create_template

_TEMPLATE_KEY = 'new_template'
_EXPORT_SCHEMA_FILE = "export_config.schema.json"
_EXPORT_SCHEMA = None

logger = logging.getLogger("configuration")


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

    data = read_file_from_directory(
        export_config_path.parent, export_config_path.name,
        "export configuration", logger, interp_ext=True)

    # validate against schema
    global _EXPORT_SCHEMA
    if _EXPORT_SCHEMA is None:
        # lazy load schema once
        _EXPORT_SCHEMA = read_file_from_directory(
            get_module_path(schema), _EXPORT_SCHEMA_FILE,
            "export configuration schema", logger, interp_ext=True)
    try:
        jsonschema.validate(data, _EXPORT_SCHEMA)
    except jsonschema.ValidationError as err:
        handle_error(
            "validation of export config {} failed against {}: {}".format(
                export_config_path, _EXPORT_SCHEMA_FILE, err.message),
            jsonschema.ValidationError, logger=logger)

    return data


def iter_all_export_infos(config_folder_paths=(),
                          regex="*.json", get_mime=False):
    """iterate through all export configuration and yield a dict of info"""
    for name, path in iter_all_export_paths(config_folder_paths, regex):
        data = load_export_config(path)

        info = dict([
            ("key", str(name)),
            ("class", data["exporter"]["class"]),
            ("path", str(path)),
            ("description", data["description"])
        ])

        if get_mime:
            info["mime_type"] = create_exporter_cls(
                data["exporter"]["class"]).output_mimetype

        yield info


def create_exporter_cls(class_str):
    # type: (str) -> nbconvert.exporters.Exporter
    """dynamically load export class"""
    export_class_path = class_str.split(".")
    module_path = ".".join(export_class_path[0:-1])
    class_name = export_class_path[-1]
    try:
        export_module = importlib.import_module(module_path)
    except ModuleNotFoundError:  # noqa: F821
        handle_error(
            "module {} containing exporter class {} not found".format(
                module_path, class_name),
                ModuleNotFoundError, logger=logger)   # noqa: F821
    if hasattr(export_module, class_name):
        export_class = getattr(export_module, class_name)
    else:
        handle_error(
            "module {} does not contain class {}".format(
                module_path, class_name), ImportError, logger=logger)

    return export_class


def get_export_extension(export_config_path):
    """return the file extension of the exporter class"""
    data = load_export_config(export_config_path)
    exporter_cls = create_exporter_cls(data["exporter"]["class"])
    return exporter_cls.file_extension


def str_to_jinja(template_str, template_key="jinja_template"):
    return DictLoader({template_key: template_str})


def load_template(template_key, template_dict):

    if template_dict is None:
        return None

    if "directory" in template_dict["outline"]:
        outline_template = read_file_from_directory(
            template_dict["outline"]["directory"],
            template_dict["outline"]["file"],
            "template outline", logger, interp_ext=False)
        outline_name = os.path.join(template_dict["outline"]["directory"],
                                    template_dict["outline"]["file"])
    else:
        outline_template = read_file_from_module(
            template_dict["outline"]["module"],
            template_dict["outline"]["file"],
            "template outline", logger, interp_ext=False)
        outline_name = os.path.join(template_dict["outline"]["module"],
                                    template_dict["outline"]["file"])

    segments = []
    for snum, segment in enumerate(template_dict.get("segments", [])):

        if "file" not in segment:
            handle_error(
                "'file' expected in segment {}".format(snum),
                KeyError, logger)

        if "directory" in segment:
            seg_data = read_file_from_directory(
                segment["directory"],
                segment["file"], "template segment", logger, interp_ext=True)
        elif "module" in segment:
            seg_data = read_file_from_module(
                segment["module"],
                segment["file"], "template segment", logger, interp_ext=True)
        else:
            handle_error(
                "'directory' or 'module' expected in segment {}".format(snum),
                KeyError, logger)

        segments.append(seg_data)

    template_str = create_template(outline_template, outline_name, segments)

    return str_to_jinja(template_str, template_key)
