import logging

from six import string_types
from traitlets.config.configurable import LoggingConfigurable

from ipypublish.utils import handle_error, pathlib

try:
    from shutil import which as exe_exists
except ImportError:
    from distutils.spawn import find_executable as exe_exists  # noqa: F401


class IPyPostProcessor(LoggingConfigurable):
    """ an abstract class for post-processors
    """

    @property
    def allowed_mimetypes(self):
        """ override in subclasses

        return a list of allowed mime types
        if None, then all are allowed

        Text based mime-types include: text/plain, text/latex, text/restructuredtext,
        text/html, text/x-python, application/json, text/markdown,
        text/asciidoc, text/yaml

        """
        raise NotImplementedError('allowed_mimetypes')

    @property
    def requires_file(self):
        """ override in subclasses

        whether the stream should be output to file (if not already)
        before processing

        return True or False
        """
        raise NotImplementedError('requires_file')

    @property
    def logger_name(self):
        """ override in subclass
        """
        return "post-processor"

    @property
    def logger(self):
        return logging.getLogger(self.logger_name)

    def __init__(self, config=None):
        super(IPyPostProcessor, self).__init__(config=config)

    def __call__(self, stream, mimetype, filepath=None):
        """
        See def postprocess() ...
        """
        self.postprocess(stream, mimetype, filepath)

    def postprocess(self, stream, mimetype, filepath,
                    resources=None, skip_mime=False):
        """ Post-process output.

        Parameters
        ----------
        stream: str
            the main file contents
        mimetype: str
            the mimetype of the file
        filepath: None or str or pathlib.Path
            the path to the output file
        resources: None or dict
            a resources dict, output from exporter.from_notebook_node   
        skip_mime:
            if False, raise a TypeError if the mimetype is not allowed,
            else return without processing

        Returns
        -------
        stream: str
        filepath: None or str or pathlib.Path

        """

        if (self.allowed_mimetypes is not None
                and mimetype not in self.allowed_mimetypes):
            if not skip_mime:
                self.handle_error(
                    "the mimetype {0} is not in the allowed list: {1}".format(
                        mimetype, self.allowed_mimetypes),
                    TypeError, self.logger)
            else:
                self.logger.debug(
                    "skipping incorrect mime type: {}".format(mimetype))
                return stream, filepath, resources

        if self.requires_file and filepath is None:
            self.handle_error(
                "the filepath is None, but the post-processor requires a file",
                TypeError, self.logger)

        if filepath is not None and isinstance(filepath, string_types):
            filepath = pathlib.Path(filepath)

        if self.requires_file:
            if filepath.exists() and not filepath.is_file():
                self.handle_error(
                    "the filepath is {} is a folder".format(filepath),
                    TypeError, self.logger)
            if not filepath.exists():
                with filepath.open("w") as fobj:
                    fobj.write(stream)

        if resources is None:
            resources = {}

        return self.run_postprocess(stream, filepath, resources)

    def run_postprocess(self, stream, filepath, resources):
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

    def handle_error(self, msg, err_type, logger,
                     raise_msg=None, log_msg=None):
        """ handle error by logging it then raising
        """
        handle_error(msg, err_type, logger,
                     raise_msg=raise_msg, log_msg=log_msg)

    def check_exe_exists(self, name, logger, msg):
        """ test if an executable exists
        """
        if not exe_exists('latexmk'):
            handle_error(msg, RuntimeError, logger)
        return True


if __name__ == "__main__":

    print(IPyPostProcessor.allowed_mimetypes)
    IPyPostProcessor()("stream", "a")
