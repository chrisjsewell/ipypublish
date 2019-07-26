""" click command for ipypublish """
import logging
import os
import sys
from mimetypes import guess_type

import click

from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline import options, utils
from ipypublish.convert.main import IpyPubMain
from ipypublish.postprocessors.reveal_serve import RevealServer


# TODO replicate argparse add_argument_group https://github.com/pallets/click/issues/373
@ipypub.command('present')
@options.INPUT_PATH
@options.OUTPUT_CONFIG(default='slides_ipypublish_main')
@options.CONFIG_PATHS()
# nb merge
@options.IGNORE_PREFIX()
# output
@options.OUTPUT_PATH()
@options.CLEAR_FILES()
# view output
@options.LAUNCH_BROWSER()
# debugging
@options.LOG_LEVEL()
@options.LOG_TRACEBACK()
@options.DRY_RUN()
def ipub_present(input_path, output_path, output_config, config_paths, ignore_prefix, clear_files, launch_browser,
                 log_level, log_traceback, dry_run):
    """Load reveal.js slides as a web server.

    If path extension is ``.ipynb`` the notebook will be converted first.

    """
    inpath_name, inpath_ext = os.path.splitext(os.path.basename(input_path))

    output_mimetype = guess_type(input_path, strict=False)[0]
    output_mimetype = 'unknown' if output_mimetype is None else output_mimetype

    if output_mimetype != 'text/html':

        config = {
            'IpyPubMain': {
                'conversion':
                output_config,
                'plugin_folder_paths':
                config_paths,
                'outpath':
                output_path,
                'ignore_prefix':
                ignore_prefix,
                'default_pporder_kwargs':
                dict(dry_run=dry_run, clear_existing=clear_files, dump_files=True, slides=True, serve_html=True),
                'log_to_stdout':
                True,
                'log_level_stdout':
                log_level,
                'log_to_file':
                True,
                'log_level_file':
                log_level,
                'log_stdout_formatter':
                utils.ColorFormatter
            }
        }
        publish = IpyPubMain(config=config)

        try:
            publish(input_path)
            click.secho('SUCCESS', fg='green', bold=True)
        except Exception:
            if log_traceback:
                # TODO this doesn't add color in stdout
                publish.logger.exception('exception raised during execution')
            click.secho('FAILURE', fg='red', bold=True)
            raise click.ClickException('exception raised during execution')

    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        server = RevealServer()
        if not dry_run:
            click.secho('SERVING...', fg='green', bold=True)
            server.postprocess('', output_mimetype, os.path.abspath(input_path))
