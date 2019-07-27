"""The main `ipypub` click group."""
import click

from ipypublish.cmdline.config import pass_config
from ipypublish.cmdline import options


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(None, '-v', '--version', message='IpyPublish version %(version)s')
@options.AUTOCOMPLETE()
@pass_config
def ipypub(config, autocomplete):
    """The command line interface of IPyPublish."""
