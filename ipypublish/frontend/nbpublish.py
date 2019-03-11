#!/usr/bin/env python
import logging
import sys

from ipypublish.frontend.shared import parse_options
from ipypublish.convert.main import IpyPubMain

logger = logging.getLogger("nbpublish")


def nbpublish(ipynb_path,
              outformat='latex_ipypublish_main',
              outpath=None, dump_files=True,
              ignore_prefix='_', clear_files=False,
              create_pdf=False,
              pdf_in_temp=False, pdf_debug=False,
              launch_browser=False,
              log_level='INFO', dry_run=False,
              print_traceback=False,
              export_paths=()):
    """ convert one or more Jupyter notebooks to a published format

    paths can be string of an existing file or folder,
    or a pathlib.Path like object

    Parameters
    ----------
    ipynb_path
        notebook file or directory
    outformat: str
        output format to use
    outpath : str or pathlib.Path
        path to output converted files
    dump_files: bool
        write files from nbconvert (containing images, etc) to outpath
    ignore_prefix: str
        ignore ipynb files with this prefix
    clear_files : str
        whether to clear existing external files in outpath folder
    create_pdf: bool
        convert to pdf (if converting to latex)
    pdf_in_temp: bool
        run pdf conversion in a temporary folder
        and only copy back the pdf file
    pdf_debug: bool
        run latexmk in interactive mode
    log_level: str
        the logging level (debug, info, critical, ...)

    """
    # run
    config = {"IpyPubMain": {
        "conversion": outformat,
        "plugin_folder_paths": export_paths,
        "outpath": outpath,
        "ignore_prefix": ignore_prefix,
        "log_to_stdout": True,
        "log_level_stdout": log_level,
        "log_to_file": True,
        "log_level_file": log_level,
        "default_pporder_kwargs": dict(
            dry_run=dry_run,
            clear_existing=clear_files,
            dump_files=dump_files,
            create_pdf=create_pdf,
        ),
        "default_ppconfig_kwargs": dict(
            pdf_in_temp=pdf_in_temp,
            pdf_debug=pdf_debug,
            launch_browser=launch_browser
        )
    }}
    publish = IpyPubMain(config=config)
    try:
        publish(ipynb_path)
    except Exception as err:
        logger.error("Run Failed: {}".format(err))
        if print_traceback:
            raise
        return 1

    return 0


def run(sys_args=None):

    if sys_args is None:
        sys_args = sys.argv[1:]

    filepath, options = parse_options(sys_args, "nbpublish")

    outcode = nbpublish(filepath, **options)

    return outcode
