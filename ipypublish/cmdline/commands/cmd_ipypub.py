"""The main `ipypub` click group."""

import click

AUTOCOMPLETE_COMMAND = 'eval "$(_IPYPUB_COMPLETE=source ipypub)"'


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(None, '-v', '--version', message='IpyPublish version %(version)s')
def ipypub():
    """The command line interface of IPyPublish."""


@ipypub.command('autocomplete')
def autocomplete():
    """ Print the terminal autocompletion command. """
    click.echo(AUTOCOMPLETE_COMMAND)
