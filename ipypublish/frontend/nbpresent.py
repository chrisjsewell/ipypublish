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
    # setup logging to terminal
    root = logging.getLogger()
    root.handlers = []  # remove any existing handlers
    root.setLevel(logging.DEBUG)
    slogger = logging.StreamHandler(sys.stdout)
    slogger.setLevel(getattr(logging, log_level.upper()))
    formatter = logging.Formatter('%(levelname)s:%(module)s:%(message)s')
    slogger.setFormatter(formatter)
    root.addHandler(slogger)

    inpath_name, inpath_ext = os.path.splitext(os.path.basename(inpath))

    outpath = None
    output_mimetype = guess_type(inpath, strict=False)[0]
    output_mimetype = 'unknown' if output_mimetype is None else output_mimetype

    if inpath_ext == '.ipynb':
        outdir = os.path.join(
            os.getcwd(), 'converted') if outpath is None else outpath
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        flogger = logging.FileHandler(os.path.join(
            outdir, inpath_name + '.nbpub.log'), 'w')
        flogger.setLevel(getattr(logging, log_level.upper()))
        root.addHandler(flogger)

        config = {"IpyPubMain": {
            "conversion": outformat,
            "plugin_folder_paths": export_paths,
            "outpath": outpath,
            "ignore_prefix": ignore_prefix
        }}
        publish = IpyPubMain(config=config,
                             dump_files=dump_files,
                             clear_existing=clear_files,
                             serve_html=True,
                             slides=True,
                             dry_run=dry_run)
        try:
            outdata = publish(inpath)

            outpath = outdata["outpath"]
            output_mimetype = outdata["exporter"].output_mimetype

        except Exception as err:
            logger.error("Run Failed: {}".format(err))
            if print_traceback:
                raise err
            return 1
    else:
        server = RevealServer()
        if not dry_run:
            server.postprocess("", output_mimetype, outpath)

    return 0


def run(sys_args=None):

    if sys_args is None:
        sys_args = sys.argv[1:]

    filepath, options = parse_options(sys_args, "nbpresent")

    outcode = nbpresent(filepath, **options)

    return outcode
