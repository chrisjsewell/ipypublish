import os
import logging
import warnings

from docutils.parsers import rst
from six import string_types
from ipypublish.utils import handle_error
from ipypublish.ipysphinx.utils import import_sphinx
from ipypublish.convert.main import publish


# TODO should inherit from sphinx.parsers.RSTParser
# https://www.sphinx-doc.org/en/master/extdev/parserapi.html
# however, sphinx is an optional dependency
class NBParser(rst.Parser):
    """Sphinx source parser for Jupyter notebooks.
    adapted from nbsphinx
    """

    supported = 'jupyter_notebook',

    def __init__(self, *args, **kwargs):

        self.app = None
        self.config = None
        self.env = None

        try:
            sphinx = import_sphinx()

            class NotebookError(sphinx.errors.SphinxError):
                """Error during notebook parsing."""

                category = 'Notebook error'

            self.error_nb = NotebookError
            self.error_config = sphinx.errors.ConfigError
            self.logger = sphinx.util.logging.getLogger('nbparser')

        except (ImportError, AttributeError):
            self.error_nb = IOError
            self.error_config = TypeError
            self.logger = logging.getLogger('nbparser')

        super(NBParser, self).__init__(*args, **kwargs)

    def set_application(self, app):
        # type: (Sphinx) -> None
        """set_application will be called from Sphinx to set app 
        and other instance variables

        Parameters
        ----------
        app: sphinx.application.Sphinx
            Sphinx application object
        """
        self.app = app
        self.config = app.config
        self.env = app.env

    def parse(self, inputstring, document):
        # type: (Union[str, StringList], nodes.document) -> None
        """Parse text and generate a document tree."""

        # fix for when calling on readthedocs
        self.env = self.env or document.settings.env
        self.config = self.config or document.settings.env.config

        # get file for conversion
        filepath = self.env.doc2path(self.env.docname)
        fileext = os.path.splitext(filepath)[1]
        filedir = os.path.dirname(filepath)
        self.logger.info("ipypublish: converting {}".format(filepath))

        # handle pre-conversion
        nbnode = None
        if fileext != ".ipynb":
            self.logger.info(
                "ipypublish: attempting pre-conversion with jupytext")
            try:
                import jupytext
            except ImportError:
                handle_error('jupytext package is not installed',
                             self.error_nb, self.logger)
            try:
                nbnode = jupytext.readf(filepath, format_name="notebook")
            except TypeError as err:  # noqa: F841
                pass
                # handle_error("jupytext: {}".format(err),
                #              self.error_nb, self.logger)

        if (fileext != ".ipynb" and nbnode is None):
            handle_error(
                'ipypublish: the file extension is not associated with any '
                'converter: {}'.format(fileext), self.error_nb, self.logger)

        # get conversion configuration
        conversion = self.config.ipysphinx_export_config
        if not isinstance(conversion, string_types):
            handle_error(
                'ipysphinx_export_config is not a string: '
                '{}'.format(conversion), self.error_config, self.logger)
        self.logger.info(
            "ipypublish: using export config {}".format(conversion))

        # type checking config values
        if not isinstance(self.config.ipysphinx_files_folder, string_types):
            handle_error(
                'ipysphinx_files_folder is not a string: '
                '{}'.format(conversion), self.error_config, self.logger)
        if not isinstance(self.config.ipysphinx_config_folders,
                          (list, set, tuple)):
            handle_error(
                'ipysphinx_config_folders is not an iterable: '
                '{}'.format(conversion), self.error_config, self.logger)

        outdata = publish(
            filepath,
            nb_node=nbnode,
            conversion=conversion,
            outpath=filedir,
            clear_existing=False,
            dump_files=True,
            files_folder=self.config.ipysphinx_files_folder,
            plugin_folder_paths=self.config.ipysphinx_config_folders
        )

        self.logger.info("ipypublish: successful conversion")

        # check we got back restructuredtext
        exporter = outdata["exporter"]
        if not exporter.output_mimetype == 'text/restructuredtext':
            handle_error(
                "ipypublish: the output content is not of type "
                "text/restructuredtext: {}".format(exporter.output_mimetype),
                TypeError, self.logger
            )

        # TODO document use of orphan
        if outdata["resources"].get("ipub", {}).get("orphan", False):
            rst.Parser.parse(self, ':orphan:', document)

        # parse a prolog
        if self.env.config.ipysphinx_prolog:
            prolog = exporter.environment.from_string(
                self.env.config.ipysphinx_prolog).render(env=self.env)
            rst.Parser.parse(self, prolog, document)

        # parse the main body of the file
        rst.Parser.parse(self, outdata["stream"], document)

        # parse an epilog
        if self.env.config.ipysphinx_epilog:
            prolog = exporter.environment.from_string(
                self.env.config.ipysphinx_epilog).render(env=self.env)
            rst.Parser.parse(self, prolog, document)
