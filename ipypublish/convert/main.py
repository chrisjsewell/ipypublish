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
from ipypublish.utils import (pathlib, handle_error,
                              get_valid_filename, find_entry_point)
from ipypublish.convert.nbmerge import merge_notebooks
from ipypublish.convert.config_manager import (get_export_config_path,
                                               load_export_config,
                                               load_template,
                                               create_exporter_cls)

logger = logging.getLogger("conversion")


def publish(ipynb_path,
            conversion='latex_ipypublish_main',
            outpath=None,
            dump_files=False,
            files_folder="{filename}_files",
            ignore_prefix='_',
            clear_existing=False,
            create_pdf=False,
            pdf_in_temp=False,
            pdf_debug=False,
            launch_browser=False,
            plugin_folder_paths=(),
            dry_run=False,
            serve_html=False):
    """ convert one or more Jupyter notebooks to a published format

    paths can be string of an existing file or folder,
    or a pathlib.Path like object

    all files linked in the documents are placed into a single files_folder

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
    files_folder: str
        the path (relative to outpath) to dump files to
        will be formated as files_folder.format(filename=filename)
        where filename is the input file name,
        stripped of its extension and sanitized
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
    outdata: dict
        containing keys;
        "outpath", "exporter", "stream", "main_filepath", "resources"

    """
    # TODO control logging and dry_run, etc through config, and related
    # (make sure this doesnt break sphinx nbparser)
    # TODO turn whole thing into a traitlets Application
    # TODO allow for parsing logger 
    # (needs to also be parsed on to called functions)

    # setup the input and output paths
    if isinstance(ipynb_path, string_types):
        ipynb_path = pathlib.Path(ipynb_path)
    ipynb_name = os.path.splitext(ipynb_path.name)[0]
    files_folder = files_folder.format(filename=get_valid_filename(ipynb_name))

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
    # Could make everything a 'PyProcess', with support for multiple streams
    final_nb, meta_path = merge_notebooks(ipynb_path,
                                          ignore_prefix=ignore_prefix)
    logger.debug('notebooks meta path: {}'.format(meta_path))

    # set post-processor defaults
    default_pproc_config = {
        "PDFExport": {
            "files_folder": files_folder,
            "convert_in_temp": pdf_in_temp,
            "debug_mode": pdf_debug,
            "open_in_browser": launch_browser,
            "skip_mime": False
        },
        "RunSphinx": {
            "open_in_browser": launch_browser,
        },
        "RemoveFolder": {
            "files_folder": files_folder
        },
        "CopyResourcePaths": {
            "files_folder": files_folder
        }
    }

    default_pprocs = [
        'remove-blank-lines',
        'remove-trailing-space',
        'filter-output-files',
        'fix-slide-refs']
    if not dry_run:
        if clear_existing:
            default_pprocs.append('remove-folder')
        default_pprocs.append('write-text-file')
        if dump_files or create_pdf or serve_html:
            default_pprocs.extend(
                ['write-resource-files', 'copy-resource-paths'])
        if create_pdf:
            default_pprocs.append('pdf-export')
        elif serve_html:
            default_pprocs.append('reveal-server')

    # load configuration file
    exporter_cls, jinja_template, econfig, pprocs, pconfig = load_config_file(
        conversion, plugin_folder_paths,
        default_pprocs, default_pproc_config,
        {"${meta_path}": str(meta_path), "${files_path}": str(files_folder)})

    # TODO do replacements separately (so configuration can be loaded earlier)

    # run nbconvert
    logger.info('running nbconvert')
    exporter, stream, resources = export_notebook(final_nb, exporter_cls,
                                                  econfig, jinja_template)

    # postprocess results
    main_filepath = os.path.join(outdir, ipynb_name + exporter.file_extension)

    for post_proc_name in pprocs:
        proc_class = find_entry_point(
            post_proc_name, "ipypublish.postprocessors", logger, "ipypublish")
        proc = proc_class(pconfig)
        stream, main_filepath, resources = proc.postprocess(
            stream, exporter.output_mimetype, main_filepath,
            resources)

    logger.info('process finished successfully')

    return {
        "outpath": outpath,
        "exporter": exporter,
        "stream": stream,
        "main_filepath": main_filepath,
        "resources": resources
    }


def load_config_file(conversion, plugin_folder_paths,
                     default_pprocs, default_pproc_config,
                     replacements):
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
    logger.info('creating process configuration')
    export_config = create_export_config(data["exporter"], template_name,
                                         replacements)
    pprocs, pproc_config = create_pproc_config(
        data.get("postprocessors", {}), default_pprocs, default_pproc_config,
        replacements)

    return exporter_cls, jinja_template, export_config, pprocs, pproc_config


def create_export_config(exporter_data, template_name, replacements):
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


def create_pproc_config(
        pproc_data, default_pprocs, default_pproc_config, replacements):
    if "order" in pproc_data:
        pprocs_list = pproc_data["order"]
    else:
        pprocs_list = default_pprocs

    pproc_config = Config(default_pproc_config)

    if "config" in pproc_data:
        override_config = pproc_data["config"]
        flat = edict.flatten(override_config)
        for instr, outstr in replacements.items():
            for key in flat:
                if isinstance(flat[key], string_types):
                    flat[key] = flat[key].replace(instr, outstr)
        override_config = edict.unflatten(flat)
        pproc_config.update(pproc_config)

    return pprocs_list, pproc_config


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
