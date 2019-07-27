import os
import click

from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline.config import pass_config
from ipypublish.cmdline import arguments, options


@ipypub.group('config')
@options.CONFIG_PATH()
@pass_config
def config(config, config_path):
    """View and set configuration options."""


@config.command('show')
@pass_config
def show(config):
    """ Print the current cli configuration options. """
    click.echo(config)


@config.command('reset')
@pass_config
def reset(config):
    """ Reset the cli configuration options. """
    click.confirm('Are you sure you want to reset the cli configuration?', abort=True)
    config.reset()
    click.secho('SUCCESS', fg='green')


@config.command('list_export_keys')
@options.FILTER_REGEX()
@options.VERBOSE()
@pass_config
def list_export_configs(config, regex, verbosity):
    """ List available export configurations. """
    from ipypublish.convert.config_manager import get_exports_info_str
    click.echo(get_exports_info_str(plugin_folder_paths=config.export_paths, regex=regex, verbosity=verbosity))


@config.command('add_export_path')
@arguments.INPUT_PATH(type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@pass_config
def add_export_path(config, input_path):
    """ Add path containing export configurations. """
    config.add_export_path(os.path.normpath(os.path.realpath(input_path)))
    click.echo('Export paths: {}'.format(config.export_paths))
    click.secho('SUCCESS', fg='green')


@config.command('list_traits')
def list_default_traits():
    """ List the default trait configuration for IpyPubMain. """
    from ipypublish.convert.main import IpyPubMain
    click.echo(IpyPubMain.class_get_help())
