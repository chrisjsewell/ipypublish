import errno
import os
import json
import io
import logging
import re
import pkg_resources

import importlib_resources
import ruamel.yaml as yaml
from six import string_types, PY2

if PY2:
    import pathlib2 as pathlib  # noqa: F401
else:
    import pathlib  # noqa: F401


def handle_error(msg='', klass=None, exception=None, logger=None):
    """handle an error, by logging it, then raising an exception"""
    if logger is None:
        logger = logging.getLogger(__name__)
    logger.error(msg)
    if exception is not None:
        raise
    else:
        raise klass(msg)


class ResourceFile(object):
    """A resource file object that can live on the file system or in a package

    """
    __slots__ = ['path', 'resource_module', 'description']

    def __init__(self, path, resource_module=None, description=''):
        self.path = path
        self.resource_module = resource_module
        self.description = ''

    @property
    def is_resource(self):
        return self.resource_module is not None

    @property
    def name(self):
        return os.path.splitext(os.path.basename(self.path))[0]

    @property
    def extension(self):
        return os.path.splitext(os.path.basename(self.path))[1]

    def __str__(self):
        if self.is_resource:
            if isinstance(self.resource_module, string_types):
                module_str = self.resource_module
            else:
                module_str = self.resource_module.__name__
            return '{}@{}'.format(self.path, module_str)
        return str(self.path)

    def get_text(self, logger):
        try:
            if self.resource_module is not None:
                text = importlib_resources.read_text(self.resource_module, self.path)
            else:
                with io.open(self.path) as handle:
                    text = handle.read()
            return text
        except Exception as err:
            handle_error('extension type not recognised: {}'.format(self), err, logger=logger)

    def get_data(self,
                 logger,
                 ext_types=(('.json', 'json'), ('.yaml', 'yaml'), ('.yaml.j2', 'yaml'), ('yaml.tex.j2', 'yaml'))):
        text = self.get_text(logger)
        ext_type = None
        ext_types = dict(ext_types)
        # Place longer extensions first to keep shorter ones from matching first
        for ext in sorted(ext_types.keys(), key=len, reverse=True):
            if self.path.endswith(ext):
                ext_type = ext_types[ext]
        if ext_type is None:
            handle_error(
                "the path's extension could not be interpreted: {}".format(self), klass=ValueError, logger=logger)
        if ext_type == 'json':
            data = json.loads(text)
        elif ext_type == 'yaml':
            data = yaml.safe_load(text)
        else:
            handle_error('extension type not recognised: {}'.format(self), klass=ValueError, logger=logger)
        return data


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def find_entry_point(name, group, logger, preferred=None):
    """find an entry point by name and group

    Parameters
    ----------
    name: str
        name of entry point
    group: str
        group of entry point
    preferred: str
        if multiple matches are found, prefer one from this module

    """
    entry_points = list(pkg_resources.iter_entry_points(group, name))
    if len(entry_points) == 0:
        handle_error(
            'The {0} entry point '
            '{1} could not be found'.format(group, name),
            klass=pkg_resources.ResolutionError,
            logger=logger)
    elif len(entry_points) != 1:
        # default to the preferred package
        oentry_points = []
        if preferred:
            oentry_points = [ep for ep in entry_points if ep.module_name.startswith(preferred)]
        if len(oentry_points) != 1:
            handle_error(
                'Multiple {0} plugins found for '
                '{1}: {2}'.format(group, name, entry_points),
                klass=pkg_resources.ResolutionError,
                logger=logger)
        logger.info('Multiple {0} plugins found for {1}, '
                    'defaulting to the {2} version'.format(group, name, preferred))
        entry_point = oentry_points[0]
    else:
        entry_point = entry_points[0]
    return entry_point.load()


def create_directory(path):
    """Attempt to create the configuration folder at the given path skipping if it already exists

    :param path: an absolute path to create a directory at
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise OSError("could not create the '{}' configuration directory".format(path))
