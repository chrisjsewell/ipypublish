import os
import json
import inspect
import importlib

from six import string_types

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
                             logger, as_json=False):
    """load a file situated in a directory

    if as_json=True load file contents to a dict

    """
    if isinstance(dir_path, string_types):
        dir_path = pathlib.Path(dir_path)

    file_path = dir_path.joinpath(file_name)

    if not file_path.exists():
        handle_error(
            "the {} does not exist: {}".format(jtype, file_path),
            IOError, logger=logger)

    if as_json:
        with file_path.open() as fobj:
            try:
                data = json.load(fobj)
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
                          logger, as_json=False):
    """load a file situated in a python module

    if as_json=True load file contents to a dict

    """
    try:
        outline_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        handle_error(
            "module {} containing {} {} not found".format(
                module_path, jtype, file_name),
            ModuleNotFoundError, logger=logger)

    return read_file_from_directory(get_module_path(outline_module),
                                    file_name, jtype, logger, as_json=as_json)
