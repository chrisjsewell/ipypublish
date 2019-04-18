import logging

from six import string_types
from traitlets import Bool
from traitlets.config.configurable import Configurable

from ipypublish.utils import handle_error, pathlib

try:
    from shutil import which as exe_exists
except ImportError:
    from distutils.spawn import find_executable as exe_exists  # noqa: F401


class IPyPostProcessor(Configurable):
    """ an abstract class for post-processors
    """

    @property
    def allowed_mimetypes(self):
        """ override in subclasses

        return a list of allowed mime types
        if None, then all are allowed

        Text based mime-types include: text/plain, text/latex,
        text/restructuredtext, text/html, text/x-python, application/json,
        text/markdown, text/asciidoc, text/yaml

        """
        raise NotImplementedError('allowed_mimetypes')

    @property
    def requires_path(self):
        """ override in subclasses

        whether the prostprocessor requires the supplied filepath
        to have an existing parent directory

        if True and filepath is None, will raise an IOError, otherwise,
        will try to make the directory if it doesn't exist

        """
        raise NotImplementedError('requires_path')

    @property
    def logger_name(self):
        """ override in subclass
        """
        return "post-processor"

    @property
    def logger(self):
        return logging.getLogger(self.logger_name)

    skip_mime = Bool(
        True,
        help="if False, raise a TypeError if the mimetype is not allowed, "
        "else return without processing").tag(config=True)

    def __init__(self, config=None):
        super(IPyPostProcessor, self).__init__(config=config)

    def __call__(self, stream, mimetype, filepath, resources=None):
        """
        See def postprocess() ...
        """
        self.postprocess(stream, mimetype, filepath, resources)

    def postprocess(self, stream, mimetype, filepath,
                    resources=None):
        """ Post-process output.

        Parameters
        ----------
        stream: str
            the main file contents
        mimetype: str
            the mimetype of the file
        filepath: None or str or pathlib.Path
            the path to the output file
            the path does not have to exist, but must be absolute
        resources: None or dict
            a resources dict, output from exporter.from_notebook_node

        Returns
        -------
        stream: str
        filepath: None or str or pathlib.Path

        """

        if (self.allowed_mimetypes is not None
                and mimetype not in self.allowed_mimetypes):
            if not self.skip_mime:
                self.handle_error(
                    "the mimetype {0} is not in the allowed list: {1}".format(
                        mimetype, self.allowed_mimetypes),
                    TypeError)
            else:
                self.logger.debug(
                    "skipping incorrect mime type: {}".format(mimetype))
                return stream, filepath, resources

        if self.requires_path and filepath is None:
            self.handle_error(
                "the filepath is None, "
                "but the post-processor requires a folder",
                IOError)

        if filepath is not None and isinstance(filepath, string_types):
            filepath = pathlib.Path(filepath)

        if self.requires_path:

            if not filepath.is_absolute():
                self.handle_error(
                    "the post-processor requires an absolute folder path",
                    IOError)

            if filepath.parent.exists() and not filepath.parent.is_dir():
                self.handle_error(
                    "the filepath's parent is not a folder: {}".format(
                        filepath),
                    TypeError)

            if not filepath.parent.exists():
                filepath.parent.mkdir(parents=True)

        if resources is None:
            resources = {}

        return self.run_postprocess(stream, mimetype, filepath, resources)

    def run_postprocess(self, stream, mimetype, filepath, resources):
        """ should not be called directly
        override in sub-class

        Parameters
        ----------
        stream: str
            the main file contents
        filepath: None or pathlib.Path
            the path to the output file
        resources: dict
            a resources dict, output from exporter.from_notebook_node

        Returns
        -------
        stream: str
        filepath: None or pathlib.Path
        resources: dict

        """
        raise NotImplementedError('run_postprocess')

    def handle_error(self, msg, err_type,
                     raise_msg=None, log_msg=None):
        """ handle error by logging it then raising
        """
        handle_error(msg, err_type, self.logger,
                     raise_msg=raise_msg, log_msg=log_msg)

    def check_exe_exists(self, name, error_msg):
        """ test if an executable exists
        """
        if not exe_exists(name):
            self.handle_error(error_msg, RuntimeError)
        return True


if __name__ == "__main__":

    print(IPyPostProcessor.allowed_mimetypes)
    IPyPostProcessor()("stream", "a")
