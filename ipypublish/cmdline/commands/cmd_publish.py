""" click command for ipypublish """
import logging
import click

from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline import options, utils


@ipypub.command('publish', cls=options.CustomCommand)
@options.INPUT_PATH
@options.OUTPUT_CONFIG(help_group='Conversion')
@options.CONFIG_PATHS(help_group='Conversion')
# nb merge
@options.IGNORE_PREFIX(help_group='Conversion')
# output
@options.OUTPUT_PATH(help_group='Output')
@options.CLEAR_FILES(help_group='Output')
@options.LAUNCH_BROWSER(help_group='Output')
# pdf export
@options.PDF_CREATE(help_group='PDF Export')
@options.PDF_IN_TEMP(help_group='PDF Export')
@options.PDF_DEBUG(help_group='PDF Export')
# debugging
@options.LOG_LEVEL(help_group='Debugging')
@options.LOG_TRACEBACK(help_group='Debugging')
@options.DRY_RUN(help_group='Debugging')
def ipub_publish(input_path, output_path, output_config, config_paths, ignore_prefix, clear_files, create_pdf,
                 pdf_in_temp, pdf_debug, launch_browser, log_level, log_traceback, dry_run):
    """Convert Jupyter notebooks to a published format.

    INPUT_PATH can be a directory or a filepath
    """
    from ipypublish.convert.config_manager import get_export_config_file
    from ipypublish.convert.main import IpyPubMain

    get_export_config_file(
        output_config,
        config_paths,
        exc_class=click.BadParameter,
        exc_kwargs={'param_hint': options.OUTPUT_CONFIG.args[1]})

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
            dict(
                dry_run=dry_run,
                clear_existing=clear_files,
                dump_files=True,
                create_pdf=create_pdf,
            ),
            'default_ppconfig_kwargs':
            dict(pdf_in_temp=pdf_in_temp, pdf_debug=pdf_debug, launch_browser=launch_browser),
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
