import os
import logging

from docutils.parsers import rst
from six import string_types
from ipypublish.utils import handle_error
from ipypublish.ipysphinx.utils import import_sphinx
from ipypublish.convert.main import publish

try:
    sphinx = import_sphinx()
    logger = sphinx.util.logging.getLogger('nbparser')
except (ImportError, AttributeError):
    logger = logging.getLogger('nbparser')


# TODO should inherit from sphinx.parsers.RSTParser
# https://www.sphinx-doc.org/en/master/extdev/parserapi.html
# however, sphinx is an optional dependency
class NBParser(rst.Parser):
    """Sphinx source parser for Jupyter notebooks.
    adapted from nbsphinx
    """

    supported = 'jupyter_notebook',

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

        # get file for conversion
        filepath = self.env.doc2path(self.env.docname)
        filedir = os.path.dirname(filepath)
        # filename = os.path.splitext(os.path.basename(filepath))[0]
        # outpath = os.path.join(filedir, filename + ".rst")
        logger.info("ipypublish: converting {}".format(filepath))

        # get conversion configuration
        conversion = self.config.ipysphinx_export_config
        if not isinstance(conversion, string_types):
            handle_error('ipysphinx_export_config is not a string: '
                         '{}'.format(conversion), TypeError, logger)
        logger.info("ipypublish: using export config {}".format(conversion))

        # type checking config values
        if not isinstance(self.config.ipysphinx_files_folder, string_types):
            handle_error('ipysphinx_files_folder is not a string: '
                         '{}'.format(conversion), TypeError, logger)
        if not isinstance(self.config.ipysphinx_config_folders,
                          (list, set, tuple)):
            handle_error('ipysphinx_config_folders is not an iterable: '
                         '{}'.format(conversion), TypeError, logger)

        outdata = publish(
            filepath,
            conversion=conversion,
            outpath=filedir,
            clear_existing=False,
            dump_files=True,
            files_folder=self.config.ipysphinx_files_folder,
            plugin_folder_paths=self.config.ipysphinx_config_folders
        )
        logger.info("ipypublish: successful conversion")

        # check we got back restructuredtext
        exporter = outdata["exporter"]
        if not exporter.output_mimetype == 'text/restructuredtext':
            handle_error(
                "ipypublish: the output content is not of type "
                "text/restructuredtext: {}".format(exporter.output_mimetype),
                TypeError, logger
            )

        # TODO document use of orphan
        if outdata["resources"].get("ipub", {}).get("orphan", False):
            rst.Parser.parse(self, ':orphan:', document)

        # parse the main body of the file
        rst.Parser.parse(self, outdata["stream"], document)
