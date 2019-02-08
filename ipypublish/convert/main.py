#!/usr/bin/env python
# import base64
from typing import List, Tuple, Union, Dict  # noqa: F401
import logging
import os
import time
from traitlets.config import Config
from jsonextended import edict
from six import string_types


import ipypublish
from ipypublish.utils import pathlib, handle_error, get_valid_filename
from ipypublish.scripts.nbmerge import merge_notebooks
from ipypublish.convert.config_manager import (get_export_config_path,
                                               load_export_config,
                                               load_template,
                                               create_exporter_cls)
from ipypublish.postprocessors.pdfexport import PDFExport

logger = logging.getLogger("conversion")


def publish(ipynb_path,
            conversion='latex_ipypublish_main',
            outpath=None,
            dump_files=False,
            ignore_prefix='_',
            clear_existing=False,
            create_pdf=False,
            pdf_in_temp=False,
            pdf_debug=False,
            launch_browser=False,
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
    pdf_browser: bool
        if True, launch webrowser of pdf
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
    files_folder = get_valid_filename(ipynb_name) + '_files'
    outdir = os.path.join(
        os.getcwd(), 'converted') if outpath is None else outpath

    # log start of conversion
    logger.info('started ipypublish v{0} at {1}'.format(
        ipypublish.__version__, time.strftime("%c")))
    logger.info('logging to: {}'.format(
        os.path.join(outdir, ipynb_name + '.nbpub.log')))
    logger.info('running for ipynb(s) at: {0}'.format(ipynb_path))
    logger.info('with conversion configuration: {0}'.format(conversion))

    # merge all notebooks (this handles checking ipynb_path exists)
    # TODO allow notebooks to remain separate
    # (would require creating a main.tex with the preamble in etc )
    final_nb, meta_path = merge_notebooks(ipynb_path,
                                          ignore_prefix=ignore_prefix)
    logger.debug('notebooks meta path: {}'.format(meta_path))

    # find conversion configuration
    logger.info('finding conversion configuration: {}'.format(conversion))
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
            IOError, logger)

    # read conversion configuration and create
    logger.info('loading conversion configuration')
    data = load_export_config(export_config_path)
    logger.info('creating exporter')
    exporter_cls = create_exporter_cls(data["exporter"]["class"])
    logger.info('creating template')
    template_name = "template_file"
    jinja_template = load_template(template_name, data["template"])
    logger.info('creating nbconvert configuration')
    config = create_config(data["exporter"], template_name,
                           {"${meta_path}": str(meta_path),
                            "${files_path}": str(files_folder)})

    # run nbconvert
    logger.info('running nbconvert')
    exporter, stream, resources = export_notebook(final_nb, exporter_cls,
                                                  config, jinja_template)

    main_filepath = os.path.join(outdir, ipynb_name + exporter.file_extension)

    # postprocess results
    from ipypublish.postprocessors.stream_modify import (
        RemoveBlankLines, RemoveTrailingSpace,
        FilterOutputFiles, FixSlideReferences
    )

    for proc_class in (RemoveBlankLines, RemoveTrailingSpace,
                       FilterOutputFiles, FixSlideReferences):
        stream, main_filepath, resources = proc_class().postprocess(
            stream, exporter.output_mimetype, main_filepath,
            resources, skip_mime=True)

    if dry_run:
        return outpath, exporter

    from ipypublish.postprocessors.file_actions import (
        RemoveFolder, WriteTextFile, WriteResourceFiles, CopyResourcePaths
    )

    if clear_existing:
        proc = RemoveFolder()
        proc.files_folder = files_folder
        stream, main_filepath, resources = proc.postprocess(
            stream, exporter.output_mimetype, main_filepath,
            resources, skip_mime=True)

    proc = WriteTextFile()
    stream, main_filepath, resources = proc.postprocess(
        stream, exporter.output_mimetype, main_filepath,
        resources, skip_mime=True)

    if dump_files or create_pdf:

        proc = WriteResourceFiles()
        stream, main_filepath, resources = proc.postprocess(
            stream, exporter.output_mimetype, main_filepath,
            resources, skip_mime=True)

        proc = CopyResourcePaths()
        proc.files_folder = files_folder
        stream, main_filepath, resources = proc.postprocess(
            stream, exporter.output_mimetype, main_filepath,
            resources, skip_mime=True)

    # create pdf
    if create_pdf:
        export_pdf = PDFExport()

        # TODO these should be passed as a configurable
        export_pdf.files_folder = files_folder
        export_pdf.convert_in_temp = pdf_in_temp
        export_pdf.debug_mode = pdf_debug
        export_pdf.open_in_browser = launch_browser

        export_pdf.postprocess(stream, exporter.output_mimetype, main_filepath)

    logger.info('process finished successfully')

    return outpath, exporter


def create_config(exporter_data, template_name, replacements):
    # type: (dict, Dict[str, str]) -> Config
    config = {}
    exporter_name = exporter_data["class"].split(".")[-1]

    config[exporter_name + ".template_file"] = template_name
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
    # this ensured that the ExtractOutputPreprocessor sets extracted files to
    # the required folder path
    # (alternatively could set resources['output_files_dir'] = files_path)
    config[
        'ExtractOutputPreprocessor.output_filename_template'
    ] = files_path + '/{unique_key}_{cell_index}_{index}{extension}'

    return _dict_to_config(config, True)


def _dict_to_config(config, unflatten=True):
    if unflatten:
        config = edict.unflatten(config, key_as_tuple=False, delim=".")
    return Config(config)


def export_notebook(final_nb, exporter_cls, config, jinja_template):

    kwargs = {"config": config}
    if jinja_template is not None:
        kwargs["extra_loaders"] = [jinja_template]
    try:
        exporter = exporter_cls(**kwargs)
    except TypeError:
        logger.warning(
            "the exporter class can not be parsed the arguments: {}".format(
                list(kwargs.keys())))
        exporter = exporter_cls()

    body, resources = exporter.from_notebook_node(final_nb)
    return exporter, body, resources


if __name__ == "__main__":
    publish("/Users/cjs14/GitHub/ipypublish/example/notebooks/Example.ipynb",
            dry_run=True)
