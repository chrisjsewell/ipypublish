import sys
from traitlets import Unicode, Enum

from ipypublish.postprocessors.base import IPyPostProcessor


class WriteStream(IPyPostProcessor):
    """ write the stream to the terminal
    """
    @property
    def allowed_mimetypes(self):
        return ("text/latex", "text/restructuredtext", "text/html",
                "text/x-python", "application/json", "text/markdown")

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "write-text-file"

    encoding = Unicode(
        default_value="utf8",
        help="the encoding of the output file"
    ).tag(config=True)

    pipe = Enum(
        ["stdout", "stderr", "stdin"],
        default_value="stdout",
        help="where to write the output to"
    ).tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):

        self.logger.info('writing stream to {}'.format(self.pipe))
        io_type = {"stdout": sys.stdout,
                   "stdin": sys.stdin,
                   "stderr": sys.stderr}.get(self.pipe)
        io_type.write(stream)

        return stream, filepath, resources
