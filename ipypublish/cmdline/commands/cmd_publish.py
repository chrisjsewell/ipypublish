""" click command for ipypublish """
import click

from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline import options, utils
from ipypublish.convert.main import IpyPubMain


# TODO replicate argparse add_argument_group https://github.com/pallets/click/issues/373
@ipypub.command('publish')
@options.INPUT_PATH
@options.OUTPUT_CONFIG()
@options.CONFIG_PATHS()
# nb merge
@options.IGNORE_PREFIX()
# output
@options.OUTPUT_PATH()
@options.CLEAR_FILES()
# pdf export
@options.PDF_CREATE()
@options.PDF_IN_TEMP()
@options.PDF_DEBUG()
# view output
@options.LAUNCH_BROWSER()
# debugging
@options.LOG_LEVEL()
@options.LOG_TRACEBACK()
@options.DRY_RUN()
def ipub_publish(input_path, output_path, output_config, config_paths, ignore_prefix, clear_files, create_pdf,
                 pdf_in_temp, pdf_debug, launch_browser, log_level, log_traceback, dry_run):
    """Convert Jupyter notebooks to a published format.

    INPUT_PATH can be a directory or a filepath
    """
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
            publish.logger.exception('exception raised during execution')
        click.secho('FAILURE', fg='red', bold=True)
        raise click.ClickException('exception raised during execution')
