#!/usr/bin/env python
import logging
import os
import sys

from ipypublish.frontend.shared import parse_options
from ipypublish.convert.main import publish

logger = logging.getLogger("nbpublish")


def nbpublish(ipynb_path,
              outformat='latex_ipypublish_main',
              outpath=None, dump_files=True,
              ignore_prefix='_', clear_files=False,
              create_pdf=False, pdf_in_temp=False, pdf_debug=False,
              log_level='INFO', dry_run=False, print_traceback=False,
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
    ipynb_name = os.path.splitext(os.path.basename(ipynb_path))[0]
    outdir = os.path.join(
        os.getcwd(), 'converted') if outpath is None else outpath
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # setup logging to terminal
    root = logging.getLogger()
    root.handlers = []  # remove any existing handlers
    root.setLevel(logging.DEBUG)
    slogger = logging.StreamHandler(sys.stdout)
    slogger.setLevel(getattr(logging, log_level.upper()))
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    slogger.setFormatter(formatter)
    slogger.propogate = False
    root.addHandler(slogger)

    # setup logging to file
    flogger = logging.FileHandler(os.path.join(
        outdir, ipynb_name + '.nbpub.log'), 'w')
    flogger.setLevel(getattr(logging, log_level.upper()))
    flogger.setFormatter(formatter)
    flogger.propogate = False
    root.addHandler(flogger)

    # run
    try:
        publish(ipynb_path,
                conversion=outformat,
                outpath=outpath, dump_files=dump_files,
                ignore_prefix=ignore_prefix, clear_existing=clear_files,
                create_pdf=create_pdf, pdf_in_temp=pdf_in_temp,
                pdf_debug=pdf_debug, dry_run=dry_run,
                plugin_folder_paths=export_paths)
    except Exception as err:
        logger.error("Run Failed: {}".format(err))
        if print_traceback:
            raise err
        return 1

    return 0


def run(sys_args=None):

    if sys_args is None:
        sys_args = sys.argv[1:]

    filepath, options = parse_options(sys_args, "nbpublish")

    outcode = nbpublish(filepath, **options)

    return outcode
