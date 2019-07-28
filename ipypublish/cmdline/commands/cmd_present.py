""" click command for ipypublish """
import logging
import os
import sys
from mimetypes import guess_type

import click

from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline.config import pass_config
from ipypublish.cmdline import arguments, options, utils


@ipypub.command('present', cls=options.CustomCommand)
@arguments.INPUT_PATH()
@options.OUTPUT_CONFIG(help_group='Conversion', default='slides_ipypublish_main', context_default=None)
@options.CONFIG_PATHS(help_group='Conversion')
# nb merge
@options.IGNORE_PREFIX(help_group='Conversion')
# output
@options.OUTPUT_PATH(help_group='Output')
@options.CLEAR_FILES(help_group='Output')
@options.LAUNCH_BROWSER(help_group='Output')
# debugging
@options.LOG_LEVEL(help_group='Debugging')
@options.LOG_TRACEBACK(help_group='Debugging')
@options.DRY_RUN(help_group='Debugging')
@pass_config
def ipub_present(config, input_path, output_path, output_config, config_paths, ignore_prefix, clear_files,
                 launch_browser, log_level, log_traceback, dry_run):
    """Load reveal.js slides as a web server.

    If path extension is ``.ipynb`` the notebook will be converted first.

    """
    from ipypublish.convert.config_manager import get_export_config_file
    from ipypublish.convert.main import IpyPubMain
    from ipypublish.postprocessors.reveal_serve import RevealServer

    config_paths = list(config.export_paths) + list(config_paths)

    get_export_config_file(
        output_config,
        config_paths,
        exc_class=click.BadParameter,
        exc_kwargs={'param_hint': options.OUTPUT_CONFIG.args[1]})

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
                logging.getLogger(__name__).exception('exception raised during execution')
            else:
                logging.getLogger(__name__).error('exception raised during execution')
            # click.secho('FAILURE', fg='red', bold=True)
            raise click.ClickException('terminating command')

    else:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        server = RevealServer()
        if not dry_run:
            click.secho('SERVING...', fg='green', bold=True)
            server.postprocess('', output_mimetype, os.path.abspath(input_path))
