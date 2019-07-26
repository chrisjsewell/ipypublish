"""The main `ipypub` click group."""

import click

from ipypublish.convert.main import IpyPubMain
from ipypublish.convert.config_manager import get_plugin_str
from ipypublish.cmdline import options


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(None, '-v', '--version', message='IpyPublish version %(version)s')
def ipypub():
    """The command line interface of IPyPublish."""


# TODO add option to print autocompletion 'eval "$(_IPYPUB_COMPLETE=source ipypub)"'


@ipypub.command('default_traits')
def ipub_default_traits():
    """ Print the default trait configuration for IpyPubMain. """
    click.echo(IpyPubMain.class_get_help())


@ipypub.command('list_configs')
@options.FILTER_REGEX()
@options.CONFIG_PATHS()
@options.VERBOSE()
def ipub_list_configs(regex, config_paths, verbose):
    """ List available export configurations. """
    click.echo(get_plugin_str(plugin_folder_paths=config_paths, regex=regex, verbose=verbose))
