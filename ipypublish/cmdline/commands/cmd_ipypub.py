"""The main `ipypub` click group."""

import click

from ipypublish.cmdline import options

AUTOCOMPLETE_COMMAND = 'eval "$(_IPYPUB_COMPLETE=source ipypub)"'


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(None, '-v', '--version', message='IpyPublish version %(version)s')
def ipypub():
    """The command line interface of IPyPublish."""


@ipypub.command('autocomplete')
def autocomplete():
    """ Print the terminal autocompletion command. """
    click.echo(AUTOCOMPLETE_COMMAND)


@ipypub.command('default_traits')
def ipub_default_traits():
    """ Print the default trait configuration for IpyPubMain. """
    from ipypublish.convert.main import IpyPubMain
    click.echo(IpyPubMain.class_get_help())


@ipypub.command('list_configs')
@options.FILTER_REGEX()
@options.CONFIG_PATHS()
@options.VERBOSE()
def ipub_list_configs(regex, config_paths, verbosity):
    """ List available export configurations. """
    from ipypublish.convert.config_manager import get_exports_info_str
    click.echo(get_exports_info_str(plugin_folder_paths=config_paths, regex=regex, verbosity=verbosity))
