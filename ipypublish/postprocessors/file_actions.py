import os
import shutil
from traitlets import Unicode, List

from ipypublish.postprocessors.base import IPyPostProcessor


class WriteTextFile(IPyPostProcessor):
    """ write the stream to a text based file
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
        "utf8",
        help="the encoding of the output file"
    ).tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):

        self.logger.info('writing stream to file: {}'.format(filepath))
        with filepath.open("w", encoding=self.encoding) as fh:
            fh.write(stream)

        return stream, filepath, resources


class RemoveFolder(IPyPostProcessor):
    """ remove a folder and all its contents
    """
    @property
    def allowed_mimetypes(self):
        return None

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "remove-folder"

    files_folder = Unicode(
        "_static",
        help="the path (relative to the main file path) to remove"
    ).tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):

        remove_folder = filepath.parent.joinpath(self.files_folder)
        if remove_folder.exists() and remove_folder.is_dir():
            self.logger.info(
                'removing folder: {0}'.format(remove_folder))
            shutil.rmtree(str(remove_folder))

        return stream, filepath, resources


class WriteResourceFiles(IPyPostProcessor):
    """ write content contained in the resources dict to file (as bytes)
    """
    @property
    def allowed_mimetypes(self):
        return None

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "write-resource-files"

    resource_keys = List(
        Unicode(),
        ["outputs"],
        help="the key names in the resources dict that contain files"
    ).tag(config=True)

    # The files already have a relative path
    # files_folder = Unicode(
    #     "_static",
    #     help="the path (relative to the main file path) to write to"
    # ).tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):

        output_folder = filepath.parent
        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        for key in self.resource_keys:
            if key not in resources:
                continue
            if not hasattr(resources[key], "items"):
                self.handle_error(
                    "the value of resources[{0}] is not a mapping".format(key),
                    TypeError)
            self.logger.info(
                'writing files in resources[{0}] to: {1}'.format(
                    key, output_folder))
            for filename, content in resources[key].items():

                outpath = output_folder.joinpath(filename)
                if not outpath.parent.exists():
                    outpath.parent.mkdir(parents=True)

                with outpath.open("wb") as fh:
                    fh.write(content)

        self.logger.debug("finished")

        return stream, filepath, resources


class CopyResourcePaths(IPyPostProcessor):
    """ copy filepaths in the resources dict to another folder
    """
    @property
    def allowed_mimetypes(self):
        return None

    @property
    def requires_path(self):
        return True

    @property
    def logger_name(self):
        return "copy-resource-paths"

    resource_keys = List(
        Unicode(),
        ["external_file_paths"],
        help="the key names in the resources dict that contain filepaths"
    ).tag(config=True)

    files_folder = Unicode(
        "_static",
        help="the path (relative to the main file path) to copy to"
    ).tag(config=True)

    def run_postprocess(self, stream, mimetype, filepath, resources):

        output_folder = filepath.parent.joinpath(self.files_folder)
        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        for key in self.resource_keys:
            if key not in resources:
                continue
            if not isinstance(resources[key], (list, tuple, set)):
                self.handle_error(
                    "the value of resources[{0}] is not an iterable".format(
                        key), TypeError)
            self.logger.info(
                'copying files in resources[{0}] to: {1}'.format(
                    key, output_folder))
            for resfilepath in resources[key]:
                shutil.copyfile(resfilepath,
                                str(output_folder.joinpath(
                                    os.path.basename(resfilepath))))

        return stream, filepath, resources
