import click

from ipypublish.cmdline.commands.cmd_ipypub import ipypub
from ipypublish.cmdline import options


@ipypub.group('config')
def config():
    """View and set configuration options."""


@config.command('list_traits')
def list_default_traits():
    """ List the default trait configuration for IpyPubMain. """
    from ipypublish.convert.main import IpyPubMain
    click.echo(IpyPubMain.class_get_help())


@config.command('list_export_keys')
@options.FILTER_REGEX()
@options.CONFIG_PATHS()
@options.VERBOSE()
def list_export_configs(regex, config_paths, verbosity):
    """ List available export configurations. """
    from ipypublish.convert.config_manager import get_exports_info_str
    click.echo(get_exports_info_str(plugin_folder_paths=config_paths, regex=regex, verbosity=verbosity))
