#!/usr/bin/env python
# import base64
from typing import List, Tuple, Union, Dict  # noqa: F401
import io
import logging
import os
import re
import shutil
import time
from traitlets.config import Config
from jsonextended import edict
from six import string_types


import ipypublish
from ipypublish.utils import pathlib
from ipypublish.scripts.nbmerge import merge_notebooks
from ipypublish.convert.config_manager import (get_export_config_path,
                                               load_export_config,
                                               load_template,
                                               create_exporter_cls)
from ipypublish.scripts.pdfexport import export_pdf


def handle_error(msg, err_type, raise_msg=None, log_msg=None):
    """handle an error, by logging it, then raising"""
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
    outpath : str or pathlib.Path
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
    export_config_path = None
    if isinstance(conversion, string_types):
        outformat_path = pathlib.Path(conversion)
    else:
        outformat_path = conversion
    if outformat_path.exists():  # TODO use pathlib approach
        # if is outformat is a path that exists, use that
        export_config_path = outformat_path
    else:
        # else search internally
        export_config_path = get_export_config_path(
            conversion, plugin_folder_paths)

    if export_config_path is None:
        handle_error(
            "could not find conversion configuration: {}".format(conversion),
            IOError)

    # read conversion configuration and create
    logging.info('loading conversion configuration')
    data = load_export_config(export_config_path)
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
