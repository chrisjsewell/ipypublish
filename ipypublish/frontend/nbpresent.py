#!/usr/bin/env python
import logging
import os
import sys

from ipypublish.frontend.shared import get_parser
from ipypublish.main import publish
from ipypublish.scripts.reveal_serve import RevealServer


def nbpresent(inpath,
              outformat='slides_standard',
              outpath=None, dump_files=True,
              ignore_prefix='_', clear_files=False,
              log_level='INFO', dry_run=False):
    """ load reveal.js slides as a web server,
    converting from ipynb first if path extension is .ipynb

    Parameters
    ----------
    inpath: str
        path to html or ipynb file
    outformat: str
        conversion format to use
    outpath : path_like
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

    if inpath_ext == '.ipynb':
        outdir = os.path.join(
            os.getcwd(), 'converted') if outpath is None else outpath
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        flogger = logging.FileHandler(os.path.join(
            outdir, inpath_name + '.nbpub.log'), 'w')
        flogger.setLevel(getattr(logging, log_level.upper()))
        root.addHandler(flogger)
        inpath, exporter = publish(inpath,
                                   conversion=outformat,
                                   outpath=outpath, dump_files=dump_files,
                                   ignore_prefix=ignore_prefix,
                                   clear_existing=clear_files,
                                   create_pdf=False, dry_run=dry_run)

    server = RevealServer()
    if not dry_run:
        server.serve(inpath)


# def list_outformats():
#     """ print list all available output formats and descriptions

#     """
#     plugins_dict = export_plugins.get()
#     outstr = 'Available Output Formats\n'
#     outstr += '------------------------'
#     for plugin_name in sorted(plugins_dict.keys()):
#         slides = plugins_dict[plugin_name]['oformat'].lower() == 'slides'
#         html = plugins_dict[plugin_name]['oformat'].lower() == 'html'
#         if not (slides or html):
#             continue
#         outstr += '\n- {}:'.format(plugin_name)
#         space = '  '
#         for line in plugins_dict[plugin_name]['descript'].split('\n'):
#             outstr += '\n' + space + line

#     return outstr


def run(sys_args):

    # TODO add option of local_plugin_dir and to list output formats

    # local_plugin_dir = os.path.join(os.getcwd(), 'ipypublish_plugins')
    # if os.path.exists(local_plugin_dir):
    #     load_errors = export_plugins.add_directory(local_plugin_dir)
    #     if load_errors:
    #         raise IOError('errors in loading external plugins: {}'.format(
    #            '\n'.join(['{0}: {1}'.format(a, b) for a, b in load_errors])))

    # plugins = export_plugins.get()

    parser = get_parser(
        description=('load reveal.js slides as a web server,\n'
                     'converting from ipynb first if path extension is ipynb'),
        # epilog=list_outformats()
    )

    parser.add_argument("filepath", type=str,
                        help='path to html or ipynb file', metavar='filepath')
    parser.add_argument("-f", "--outformat", type=str,
                        metavar='key | filepath',
                        # choices=list(plugins.keys()),
                        help='output format configuration to use',
                        default='slides_ipypublish_main')
    parser.add_argument("-o", "--outpath", type=str, metavar='str',
                        help='path to output converted files',
                        default=os.path.join(os.getcwd(), 'converted'))
    # parser.add_argument("-d","--dump-files", action="store_true",
    #                     help='dump external files, '
    #                          'linked to in the document, into the outpath')
    parser.add_argument("-c", "--clear-files", action="store_true",
                        help='clear any external files '
                        'that already exist in the outpath')
    parser.add_argument("-log", "--log-level", type=str, default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help='the logging level to output to screen/file')
    parser.add_argument("-dr", "--dry-run", action="store_true",
                        help=("perform a 'dry run', "
                              "which will not output any files"))
    args = parser.parse_args(sys_args)

    options = vars(args)
    filepath = options.pop('filepath')
    nbpresent(filepath, **options)
