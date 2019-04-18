import os
import logging
from typing import Union  # noqa: F401

from docutils import nodes  # noqa E501
from docutils.parsers import rst
from ipypublish.utils import handle_error
from ipypublish.sphinx.utils import import_sphinx
from ipypublish.convert.main import IpyPubMain


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
        # type: (Union[str, list[str]], nodes.document) -> None
        """Parse text and generate a document tree."""

        # fix for when calling on readthedocs
        self.env = self.env or document.settings.env
        self.config = self.config or document.settings.env.config

        # get file for conversion
        filepath = self.env.doc2path(self.env.docname)
        filedir = os.path.dirname(filepath)
        self.logger.info("ipypublish: converting {}".format(filepath))

        config = {"IpyPubMain": {
            "conversion": self.config.ipysphinx_export_config,
            "plugin_folder_paths": self.config.ipysphinx_config_folders,
            "outpath": filedir,
            "folder_suffix": self.config.ipysphinx_folder_suffix,
            "log_to_stdout": False,
            "log_to_file": False,
            "default_pporder_kwargs": dict(
                clear_existing=False,
                dump_files=True)
        }}
        if self.config.ipysphinx_preconverters:
            # NB: jupytext is already a default for .Rmd
            config["IpyPubMain"]["pre_conversion_funcs"] = (
                self.config.ipysphinx_preconverters)
        publish = IpyPubMain(config=config)
        outdata = publish(filepath)

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
