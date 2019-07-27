"""Module with pre-defined reusable commandline options that can be used as `click` decorators."""
from collections import OrderedDict
import os
import click

from ipypublish.cmdline import config as ipub_config


class IpubOption(click.Option):
    """ This extends ``click.Option`` by:

    - including a ``help_group`` attribute, to group options in the help text,
      see: https://github.com/pallets/click/issues/373
    - including a ``context_default`` attribute, to set the default *via* the ``ctx.obj``
      Note: this takes priority over ``default``

    """

    def __init__(self, *args, **kwargs):
        self.help_group = kwargs.pop('help_group', None)
        self.context_default = kwargs.pop('context_default', None)
        super(IpubOption, self).__init__(*args, **kwargs)

    def get_default(self, ctx):
        if self.context_default is not None:
            try:
                self.default = ctx.obj[self.context_default]
            except (TypeError, KeyError):
                pass
        return super(IpubOption, self).get_default(ctx)


class CustomCommand(click.Command):
    """ This extends the ``click.Command`` by:

    - allowing Options to be grouped in the help text by a ``help_group`` attribute,
      see: https://github.com/pallets/click/issues/373
    - call ``Option.default = Option.get_default()`` before creating the parameter help

    """

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        opts = OrderedDict()
        for param in self.get_params(ctx):
            try:
                param.default = param.get_default(ctx)
            except (TypeError, KeyError):
                pass
            rv = param.get_help_record(ctx)
            if rv is not None:
                if hasattr(param, 'help_group') and param.help_group:
                    opts.setdefault(str(param.help_group), []).append(rv)
                else:
                    opts.setdefault('Options', []).append(rv)

        for name, opts_group in opts.items():
            with formatter.section(name):
                formatter.write_dl(opts_group)


class OverridableOption(object):  # pylint: disable=useless-object-inheritance
    """
    Wrapper around click option that increases reusability

    Click options are reusable already but sometimes it can improve the user interface to for example customize a
    help message for an option on a per-command basis. Sometimes the option should be prompted for if it is not given
    On some commands an option might take any folder path, while on another the path only has to exist.

    Overridable options store the arguments to OverridableOption and only instantiate the OverridableOption on call,
    kwargs given to ``__call__`` override the stored ones.

    Example::

        FOLDER = OverridableOption('--folder', type=click.Path(file_okay=False), help='A folder')

        @click.command()
        @FOLDER(help='A folder, will be created if it does not exist')
        def ls_or_create(folder):
            click.echo(os.listdir(folder))

        @click.command()
        @FOLDER(help='An existing folder', type=click.Path(exists=True, file_okay=False, readable=True)
        def ls(folder)
            click.echo(os.listdir(folder))
    """

    def __init__(self, *args, **kwargs):
        """
        Store the default args and kwargs.

        :param args: default arguments to be used for the click option
        :param kwargs: default keyword arguments to be used that can be overridden in the call
        """
        self.args = args
        self.kwargs = kwargs
        if 'cls' not in self.kwargs:
            self.kwargs['cls'] = IpubOption

    def __call__(self, **kwargs):
        """
        Override the stored kwargs, (ignoring args as we do not allow option name changes) and return the option.

        :param kwargs: keyword arguments that will override those set in the construction
        :return: click option constructed with args and kwargs defined during construction and call of this instance
        """
        kw_copy = self.kwargs.copy()
        kw_copy.update(kwargs)
        return click.option(*self.args, **kw_copy)

    def clone(self, **kwargs):
        """
        Create a new instance of the OverridableOption by cloning it and updating the stored kwargs with those passed.

        :param kwargs: keyword arguments to update
        :return: OverridableOption instance with stored keyword arguments updated
        """
        import copy
        clone = copy.deepcopy(self)
        clone.kwargs.update(kwargs)
        return clone


_AUTOCOMPLETE_COMMAND = 'eval "$(_IPYPUB_COMPLETE=source ipypub)"'


def callback_autocomplete(ctx, param, value):
    if value and not ctx.resilient_parsing:
        click.echo(_AUTOCOMPLETE_COMMAND)
        ctx.exit()


AUTOCOMPLETE = OverridableOption(
    '-a',
    '--autocomplete',
    help='Print the terminal autocompletion command and exit.',
    is_flag=True,
    expose_value=True,
    is_eager=True,
    callback=callback_autocomplete)


def callback_config_path(ctx, param, value):
    if value and not ctx.resilient_parsing:
        try:
            click.echo(ctx.obj.file_path)
        except AttributeError:
            raise click.BadOptionUsage(
                param, 'The IpubClickConfig object has not been passed to the command: {}'.format(ctx.__dict__))
        ctx.exit()


CONFIG_PATH = OverridableOption(
    '-f',
    '--file-path',
    'config_path',
    help='Print the configuration file path and exit.',
    is_flag=True,
    expose_value=True,
    is_eager=True,
    callback=callback_config_path)

# CONFIG_PATHS = OverridableOption(
#     '-ep',
#     '--export-paths',
#     'config_paths',
#     metavar='PATH',
#     multiple=True,
#     type=click.Path(exists=True, file_okay=False, dir_okay=True),
#     help=('Add additional folder paths, '
#           'containing export configurations.'))

CLEAR_FILES = OverridableOption(
    '-c',
    '--clear-files',
    'clear_files',
    is_flag=True,
    default=False,
    show_default=True,
    help=('Clear any external files '
          'that already exist in the outpath.'))

DRY_RUN = OverridableOption(
    '-dr',
    '--dry-run',
    'dry_run',
    is_flag=True,
    default=False,
    show_default=True,
    help=("perform a 'dry run', which will not output any files"))

FILTER_REGEX = OverridableOption('-r', '--filter-regex', 'regex', default=None, help='Filter by a regex.')

IGNORE_PREFIX = OverridableOption(
    '-i',
    '--ignore-prefix',
    'ignore_prefix',
    default='_',
    show_default=True,
    help='When merging notebooks, ignore ipynb files with this prefix.')

LAUNCH_BROWSER = OverridableOption(
    '-lb',
    '--launch-browser',
    'launch_browser',
    is_flag=True,
    default=False,
    show_default=True,
    help=('Open the output in an available web-browser.'))

LOG_LEVEL = OverridableOption(
    '-log',
    '--log-level',
    'log_level',
    default='info',
    show_default=True,
    type=click.Choice(('debug', 'info', 'warning', 'error'), case_sensitive=False),
    help='The logging level to output to screen/file.')

LOG_TRACEBACK = OverridableOption(
    '-pt/-no-pt',
    '--print-traceback',
    'log_traceback',
    is_flag=True,
    default=True,
    show_default=True,
    help=('Log the full exception traceback'))

OUTPUT_PATH = OverridableOption(
    '-o',
    '--outpath',
    'output_path',
    default=os.path.join(os.getcwd(), 'converted'),
    help='Path to output converted files.',
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True))


def autocompletion_export_config(ctx, args, incomplete):
    from ipypublish.convert.config_manager import iter_all_export_files
    # TODO ctx.obj is not getting passed (so completions do not contain those in export_paths)
    try:
        export_paths = ctx.obj[ipub_config.KEY_EXPORT_PATHS]
    except (TypeError, KeyError):
        export_paths = ()
    possibilities = [f.name for f in iter_all_export_files(export_paths) if f.name.startswith(incomplete)]

    return list(possibilities)


OUTPUT_CONFIG = OverridableOption(
    '-f',
    '--outformat',
    'output_config',
    metavar='KEY|PATH',
    default='latex_ipypublish_main',
    context_default=ipub_config.KEY_DEFAULT_EXPORT_CONFIG,
    show_default=True,
    autocompletion=autocompletion_export_config,
    help=('Export format configuration to use, '
          'can be a key name or path to the file.'))

PDF_CREATE = OverridableOption(
    '-pdf',
    '--create-pdf',
    'create_pdf',
    is_flag=True,
    default=False,
    show_default=True,
    help=('Convert to pdf (only if latex exporter).'))

PDF_IN_TEMP = OverridableOption(
    '-ptemp',
    '--pdf-in-temp',
    'pdf_in_temp',
    is_flag=True,
    default=False,
    show_default=True,
    help=('Run pdf conversion in a temporary folder'
          ' and only copy back the .pdf file.'))

PDF_DEBUG = OverridableOption(
    '-pbug',
    '--pdf-debug',
    'pdf_debug',
    is_flag=True,
    default=False,
    show_default=True,
    help=('Run pdf conversion in a temporary folder'
          ' and only copy back the .pdf file.'))

VERBOSE = OverridableOption('-v', '--verbosity', count=True, help='Verbosity level of output (-v=1, -vv=2, ...).')
