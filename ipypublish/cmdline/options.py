"""Module with pre-defined reusable commandline options that can be used as `click` decorators."""
from collections import OrderedDict
import os
import click


class CustomOption(click.Option):
    """ a ``click.Option`` subclass that includes a ``help_group`` attribute"""

    def __init__(self, *args, **kwargs):
        self.help_group = kwargs.pop('help_group', None)
        super(CustomOption, self).__init__(*args, **kwargs)


class CustomCommand(click.Command):
    """ a ``click.Command`` subclass that allows help options to be grouped by a ``help_group`` attribute"""

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        opts = OrderedDict()
        for param in self.get_params(ctx):
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
            self.kwargs['cls'] = CustomOption

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


CONFIG_PATHS = OverridableOption(
    '-ep',
    '--export-paths',
    'config_paths',
    metavar='PATH',
    multiple=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help=('Add additional folder paths, '
          'containing export configurations.'))

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

INPUT_PATH = click.argument('input_path', type=click.Path(exists=True, file_okay=True, dir_okay=True, allow_dash=False))

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

# TODO add dynamic autocompletion (with cache), when https://github.com/click-contrib/click-completion/pull/27 is merged
OUTPUT_CONFIG = OverridableOption(
    '-f',
    '--outformat',
    'output_config',
    metavar='KEY|PATH',
    default='latex_ipypublish_main',
    show_default=True,
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
