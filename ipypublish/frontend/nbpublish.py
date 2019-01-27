#!/usr/bin/env python
import logging
import os
import sys

from ipypublish.frontend.shared import get_parser
from ipypublish.main import publish


def nbpublish(ipynb_path,
              outformat='latex_ipypublish_main',
              outpath=None, dump_files=True,
              ignore_prefix='_', clear_files=False,
              create_pdf=False, pdf_in_temp=False, pdf_debug=False,
              log_level='INFO', dry_run=False):
    """ convert one or more Jupyter notebooks to a published format

    paths can be string of an existing file or folder,
    or a pathlib.Path like object

    Parameters
    ----------
    ipynb_path
        notebook file or directory
    outformat: str
        output format to use
    outpath : path_like
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
    formatter = logging.Formatter('%(levelname)s:%(module)s:%(message)s')
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
    return publish(ipynb_path,
                   conversion=outformat,
                   outpath=outpath, dump_files=dump_files,
                   ignore_prefix=ignore_prefix, clear_existing=clear_files,
                   create_pdf=create_pdf, pdf_in_temp=pdf_in_temp,
                   pdf_debug=pdf_debug, dry_run=dry_run)


# def list_outformats():
#     """ print list all available output formats and descriptions

#     """
#     plugins_dict = export_plugins.get()
#     outstr = 'Available Output Formats\n'
#     outstr += '------------------------'
#     for plugin_name in sorted(plugins_dict.keys()):
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
        description=('convert one or more Jupyter notebooks '
                     'to a publishable format'),
        # epilog=list_outformats()
    )
    parser.add_argument("filepath", type=str,
                        help='notebook file or directory', metavar='filepath')
    parser.add_argument("-f", "--outformat", type=str,
                        metavar='key | filepath',
                        # choices=list(plugins.keys()),
                        help='output format configuration to use',
                        default='latex_ipypublish_main')
    parser.add_argument("-o", "--outpath", type=str, metavar='str',
                        help='path to output converted files',
                        default=os.path.join(os.getcwd(), 'converted'))
    # parser.add_argument("-d","--dump-files", action="store_true",
    #                     help='dump external files, '
    #                          'linked to in the document, into the outpath')
    parser.add_argument("-c", "--clear-files", action="store_true",
                        help=('clear any external files'
                              'that already exist in the outpath'))
    parser.add_argument("-i", "--ignore-prefix", type=str, metavar='str',
                        help='ignore ipynb files with this prefix',
                        default='_')
    parser.add_argument("-pdf", "--create-pdf", action="store_true",
                        help='convert to pdf (only if converting to latex)')
    parser.add_argument("-ptemp", "--pdf-in-temp", action="store_true",
                        help=('run pdf conversion in a temporary folder '
                              'and only copy back the .pdf file'))
    parser.add_argument("-pbug", "--pdf-debug", action="store_true",
                        help='run latexmk in interactive mode')
    parser.add_argument("-log", "--log-level", type=str, default='info',
                        choices=['debug', 'info', 'warning', 'error'],
                        help='the logging level to output to screen/file')
    parser.add_argument("-dr", "--dry-run", action="store_true",
                        help=("perform a 'dry run', "
                              "which will not output any files"))

    args = parser.parse_args(sys_args)

    options = vars(args)
    filepath = options.pop('filepath')
    return nbpublish(filepath, **options)
