import os
import json
import inspect
import importlib

from six import string_types
import yaml  # TODO use ruamel.yaml instead?

# python 2/3 compatibility
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


def handle_error(msg, err_type, logger, raise_msg=None, log_msg=None):
    """handle an error, by logging it, then raising an exception"""
    if raise_msg is None:
        raise_msg = msg
    if log_msg is None:
        log_msg = msg

    logger.error(log_msg)
    raise err_type(raise_msg)


def read_file_from_directory(dir_path, file_name, jtype,
                             logger, interp_ext=False,
                             ext_types=(
                                 ("json", (".json",)),
                                 ("yaml", (".yaml", ".yaml.j2")))):
    """load a file situated in a directory

    if ``interp_ext=True``:
    interpret the file extension *via* ``ext_types``
    and load file in a suitable manner

    """
    if isinstance(dir_path, string_types):
        dir_path = pathlib.Path(dir_path)

    file_path = dir_path.joinpath(file_name)

    if not file_path.exists():
        handle_error(
            "the {} does not exist: {}".format(jtype, file_path),
            IOError, logger=logger)

    ext_type = None
    ext_map = {ext: ftype for ftype, exts in ext_types for ext in exts}
    # Place longer extensions first to keep shorter ones from matching first
    for ext in sorted(ext_map.keys(), key=len, reverse=True):
        if file_name.endswith(ext):
            ext_type = ext_map[ext]

    if ext_type is not None and interp_ext:
        with file_path.open() as fobj:
            try:
                if ext_type == "json":
                    data = json.load(fobj)
                elif ext_type == "yaml":
                    data = yaml.safe_load(fobj)
                else:
                    raise ValueError("extension type not recognised")
            except Exception as err:
                handle_error("failed to read {} ({}): {}".format(
                    jtype, file_path, err), IOError, logger=logger)
    else:
        with file_path.open() as fobj:
            data = fobj.read()

    return data


def get_module_path(module):
    """return a directory path to a module"""
    return pathlib.Path(os.path.dirname(
        os.path.abspath(inspect.getfile(module))))


def read_file_from_module(module_path, file_name, jtype,
                          logger, interp_ext=False,
                          ext_types=(
                              ("json", (".json")),
                              ("yaml", (".yaml", ".yaml.j2")))):
    """load a file situated in a python module

    if ``interp_ext=True``:
    interpret the file extension *via* ``ext_type``
    and load file in a suitable manner

    """
    try:
        outline_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        handle_error(
            "module {} containing {} {} not found".format(
                module_path, jtype, file_name),
            ModuleNotFoundError, logger=logger)

    return read_file_from_directory(get_module_path(outline_module),
                                    file_name, jtype, logger,
                                    interp_ext=interp_ext,
                                    ext_types=ext_types)
