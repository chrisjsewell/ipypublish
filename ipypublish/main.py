#!/usr/bin/env python
# import base64
from ipypublish.scripts.create_template import create_template
import importlib
import glob
import inspect
from typing import List, Tuple, Union, Dict  # noqa: F401
import io
import logging
import os
import re
import shutil
import time
import json
from traitlets.config import Config
from jinja2 import DictLoader
from jsonextended import edict
from six import string_types


import ipypublish
from ipypublish.utils import pathlib
from ipypublish.scripts.nbmerge import merge_notebooks
from ipypublish.scripts.pdfexport import export_pdf
from ipypublish import export_plugins

_TEMPLATE_KEY = 'new_template'


def handle_error(msg, err_type, raise_msg=None, log_msg=None):

    if raise_msg is None:
        raise_msg = msg
    if log_msg is None:
        log_msg = msg

    logging.error(log_msg)
    raise err_type(raise_msg)


def publish(ipynb_path,
            conversion='latex_ipypublish_main',
            outpath=None,
            dump_files=False,
            ignore_prefix='_',
            clear_existing=False,
            create_pdf=False,
            pdf_in_temp=False,
            pdf_debug=False,
            plugin_folder_paths=(),
            dry_run=False):
    """ convert one or more Jupyter notebooks to a published format

    paths can be string of an existing file or folder,
    or a pathlib.Path like object

    all files linked in the documents are placed into a single folder

    Parameters
    ----------
    ipynb_path
        notebook file or directory
    outformat: str
        output format to use
    outpath : path_like
        path to output converted files
    dump_files: bool
        whether to write files from nbconvert (images, etc) to outpath
    ignore_prefix: str
        ignore ipynb files with this prefix
    clear_existing : str
        whether to clear existing external files in outpath folder
    create_pdf: bool
        whether to convert to pdf (if converting to latex)
    pdf_in_temp: bool
        whether to run pdf conversion in a temporary folder
    pdf_debug: bool
        if True, run latexmk in interactive mode
    dry_run: bool
        if True, do not create any files

    Returns
    --------
    outpath: str
        path to output file
    exporter: nbconvert.exporters.Exporter
        the exporter used

    """
    # setup the input and output paths
    if isinstance(ipynb_path, string_types):
        ipynb_path = pathlib.Path(ipynb_path)
    ipynb_name = os.path.splitext(ipynb_path.name)[0]
    files_folder = ipynb_name + '_files'
    outdir = os.path.join(
        os.getcwd(), 'converted') if outpath is None else outpath

    if not dry_run and not os.path.exists(outdir):
        os.mkdir(outdir)

    # log start of conversion
    logging.info('started ipypublish v{0} at {1}'.format(
        ipypublish.__version__, time.strftime("%c")))
    logging.info('logging to: {}'.format(
        os.path.join(outdir, ipynb_name + '.nbpub.log')))
    logging.info('running for ipynb(s) at: {0}'.format(ipynb_path))
    logging.info('with conversion configuration: {0}'.format(conversion))

    # merge all notebooks (this handles checking ipynb_path exists)
    final_nb, meta_path = merge_notebooks(ipynb_path,
                                          ignore_prefix=ignore_prefix)
    logging.debug('notebooks meta path: {}'.format(meta_path))

    # find conversion configuration
    logging.info('finding conversion configuration: {}'.format(conversion))
    plugin_path = None
    if isinstance(conversion, string_types):
        outformat_path = pathlib.Path(conversion)
    else:
        outformat_path = conversion
    if outformat_path.exists():  # TODO use pathlib approach
        # if is outformat is a path that exists, use that
        plugin_path = outformat_path
    else:
        # else search internally
        plugin_path = get_plugin_path(conversion, plugin_folder_paths)

    if plugin_path is None:
        handle_error(
            "could not find conversion configuration: {}".format(conversion),
            IOError)

    # read conversion configuration and create
    logging.info('loading conversion configuration')
    data = load_plugin(plugin_path)
    logging.info('creating exporter')
    exporter_cls = create_exporter_cls(data["exporter"]["class"])
    logging.info('creating template')
    jinja_template = load_template(data["template"])
    logging.info('creating nbconvert configuration')
    config = create_config(data["exporter"],
                           {"${meta_path}": str(meta_path),
                            "${files_path}": str(files_folder)})

    # run nbconvert
    logging.info('running nbconvert')
    exporter, body, resources = export_notebook(final_nb, exporter_cls,
                                                config, jinja_template)

    # postprocess results
    body, resources, internal_files = postprocess_nb(body, resources)

    if dry_run:
        return outpath, exporter

    # write results
    logging.info("writing results")
    main_file_name = ipynb_name + exporter.file_extension
    outpath, outfilespath = write_output(body, resources, outdir,
                                         main_file_name,
                                         dump_files or create_pdf,
                                         files_folder, internal_files,
                                         clear_existing)

    # create pdf
    if create_pdf and exporter.output_mimetype == 'text/latex':
        logging.info('running pdf conversion')

        if not export_pdf(outpath, outdir=outdir,
                          files_path=outfilespath,
                          convert_in_temp=pdf_in_temp,
                          html_viewer=True,
                          debug_mode=pdf_debug):
            handle_error('pdf export failed, try running with pdf_debug=True',
                         RuntimeError)

    logging.info('process finished successfully')

    return outpath, exporter


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


def str_to_jinja(template_str):
    return DictLoader({_TEMPLATE_KEY: template_str})


def create_config(exporter_data, replacements):
    # type: (dict, Dict[str, str]) -> Config
    config = {}
    exporter_name = exporter_data["class"].split(".")[-1]
    config[exporter_name + ".filters"] = exporter_data.get("filters", [])

    preprocessors = []
    for preproc in exporter_data.get("preprocessors", []):
        preprocessors.append(preproc["class"])
        preproc_name = preproc["class"].split(".")[-1]
        for name, val in preproc.get("args", {}).items():
            if isinstance(val, string_types):
                for instr, outstr in replacements.items():
                    val = val.replace(instr, outstr)
            config[preproc_name + "." + name] = val
    config[exporter_name + ".preprocessors"] = preprocessors

    for name, val in exporter_data.get("other_args", {}).items():
        if isinstance(val, string_types):
            for instr, outstr in replacements.items():
                val = val.replace(instr, outstr)
        config[name] = val

    # ensure file paths point towards the right folder
    files_path = "${files_path}"
    for instr, outstr in replacements.items():
        files_path = files_path.replace(instr, outstr)
    config[
        'ExtractOutputPreprocessor.output_filename_template'
    ] = files_path + '/{unique_key}_{cell_index}_{index}{extension}'

    return dict_to_config(config, True)


def dict_to_config(config, unflatten=True):
    if unflatten:
        config = edict.unflatten(config, key_as_tuple=False, delim=".")
    return Config(config)


def export_notebook(final_nb, exporter_cls, config, jinja_template):
    exporter = exporter_cls(
        config=config,
        extra_loaders=[] if jinja_template is None else [jinja_template])
    body, resources = exporter.from_notebook_node(final_nb)
    return exporter, body, resources


def postprocess_nb(body, resources):
    # TODO could this be written as nbconvert component?

    # reduce multiple blank lines to single
    body = re.sub(r'\n\s*\n', '\n\n', body)
    # make sure references refer to correct slides
    if 'refslide' in resources:
        for k, (col, row) in resources['refslide'].items():
            body = body.replace('{{id_home_prefix}}{0}'.format(
                k), '#/{0}/{1}{2}'.format(col, row, k))

    # filter internal files by those that are referenced in the document body
    if resources['outputs']:
        for path in list(resources['outputs'].keys()):
            if path not in body:
                resources['outputs'].pop(path)
        internal_files = resources['outputs']
    else:
        internal_files = {}

    return body, resources, internal_files


def write_output(body, resources, outdir, main_file_name, output_external,
                 files_folder, internal_files, clear_existing):
    # TODO should this be done using an nbconvert writer?
    # e.g. nbconvert.writers.FilesWriter

    # output main file
    outpath = os.path.join(outdir, main_file_name)
    outfilespath = os.path.join(outdir, files_folder)

    logging.info('outputting converted file to: {}'.format(outpath))
    with io.open(outpath, "w", encoding='utf8') as fh:
        fh.write(body)

    # output external files
    if output_external:
        logging.info('dumping external files to: {}'.format(outfilespath))

        if os.path.exists(outfilespath):
            if clear_existing:
                shutil.rmtree(outfilespath)
        else:
            os.mkdir(outfilespath)

        for internal_path, fcontents in internal_files.items():
            with open(os.path.join(outdir, internal_path), "wb") as fh:
                fh.write(fcontents)
        for external_path in resources['external_file_paths']:
            shutil.copyfile(external_path,
                            os.path.join(outfilespath,
                                         os.path.basename(external_path)))

    return outpath, outfilespath


if __name__ == "__main__":
    publish("/Users/cjs14/GitHub/ipypublish/example/notebooks/Example.ipynb",
            dry_run=True)
