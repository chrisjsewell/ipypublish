"""
postprocessors that modify the output stream
"""
import re

from ipypublish.postprocessors.base import IPyPostProcessor


class RemoveBlankLines(IPyPostProcessor):
    """ remove multiple lines of blank space """
    @property
    def allowed_mimetypes(self):
        return ("text/latex", "text/restructuredtext", "text/html",
                "text/x-python", "application/json", "text/markdown")

    @property
    def requires_path(self):
        return False

    @property
    def logger_name(self):
        return "remove-blank-lines"

    def run_postprocess(self, stream, mimetype, filepath, resources):
        stream = re.sub(r'\n\s*\n', '\n\n', stream)
        return stream, filepath, resources


class RemoveTrailingSpace(IPyPostProcessor):
    """ remove trailing whitespace on each line """
    @property
    def allowed_mimetypes(self):
        return ("text/latex", "text/restructuredtext",
                "text/x-python", "application/json", "text/markdown")

    @property
    def requires_path(self):
        return False

    @property
    def logger_name(self):
        return "remove-trailing-space"

    def run_postprocess(self, stream, mimetype, filepath, resources):
        stream = "\n".join([l.rstrip() for l in stream.splitlines()])
        return stream, filepath, resources


class FilterOutputFiles(IPyPostProcessor):
    """ filter internal files in resources['outputs'],
    by those that are referenced in the stream """
    @property
    def allowed_mimetypes(self):
        return None

    @property
    def requires_path(self):
        return False

    @property
    def logger_name(self):
        return "filter-output-files"

    def run_postprocess(self, stream, mimetype, filepath, resources):

        if 'outputs' in resources:
            for path in list(resources['outputs'].keys()):
                if path not in stream:
                    resources['outputs'].pop(path)

        return stream, filepath, resources


class FixSlideReferences(IPyPostProcessor):
    """ make sure references refer to correct slides """
    @property
    def allowed_mimetypes(self):
        return ("text/html")

    @property
    def requires_path(self):
        return False

    @property
    def logger_name(self):
        return "fix-slide-refs"

    def run_postprocess(self, stream, mimetype, filepath, resources):
        if resources and 'refslide' in resources:
            for k, (col, row) in resources['refslide'].items():
                stream = stream.replace('{{id_home_prefix}}{0}'.format(
                    k), '#/{0}/{1}{2}'.format(col, row, k))
        return stream, filepath, resources
