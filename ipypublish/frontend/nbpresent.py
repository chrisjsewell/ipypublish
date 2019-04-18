#!/usr/bin/env python
import logging
import os
import sys
from mimetypes import guess_type

from ipypublish.frontend.shared import parse_options
from ipypublish.convert.main import IpyPubMain
from ipypublish.postprocessors.reveal_serve import RevealServer

logger = logging.getLogger("nbpresent")


def nbpresent(inpath,
              outformat='slides_standard',
              outpath=None, dump_files=True,
              ignore_prefix='_', clear_files=False,
              log_level='INFO', dry_run=False,
              print_traceback=False,
              export_paths=()):
    """ load reveal.js slides as a web server,
    converting from ipynb first if path extension is .ipynb

    Parameters
    ----------
    inpath: str
        path to html or ipynb file
    outformat: str
        conversion format to use
    outpath : str  or pathlib.Path
        path to output converted files
    dump_files: bool
        whether to write files from nbconvert (images, etc) to outpath
    clear_files : str
        whether to clear existing external files in outpath folder
    ignore_prefix: str
        ignore ipynb files with this prefix
    log_level: str
        the logging level (debug, info, critical, ...)

    """
    inpath_name, inpath_ext = os.path.splitext(os.path.basename(inpath))

    output_mimetype = guess_type(inpath, strict=False)[0]
    output_mimetype = 'unknown' if output_mimetype is None else output_mimetype

    if output_mimetype != "text/html":

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
                serve_html=True,
                slides=True
            )
        }}
        publish = IpyPubMain(config=config)
        try:
            outdata = publish(inpath)

            outpath = outdata["outpath"]
            output_mimetype = outdata["exporter"].output_mimetype

        except Exception as err:
            logger.error("Run Failed: {}".format(err))
            if print_traceback:
                raise
            return 1
    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        server = RevealServer()
        if not dry_run:
            server.postprocess("", output_mimetype, os.path.abspath(inpath))

    return 0


def run(sys_args=None):

    if sys_args is None:
        sys_args = sys.argv[1:]

    filepath, options = parse_options(sys_args, "nbpresent")

    outcode = nbpresent(filepath, **options)

    return outcode
