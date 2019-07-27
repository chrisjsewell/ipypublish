import copy
import io
import os

import click
import six

APP_NAME = 'IpyPublish'
CONFIG_FILENAME = '.ipypub_config.yaml'

KEY_EXPORT_PATHS = 'export_paths'
KEY_DEFAULT_EXPORT_CONFIG = 'default_export_config'
CONFIG_DEFAULTS = {KEY_DEFAULT_EXPORT_CONFIG: 'latex_ipypublish_main', KEY_EXPORT_PATHS: []}


def validate_config(config, path):
    import jsonschema
    schema = {
        '$schema': 'http://json-schema.org/draft-07/schema',
        'type': 'object',
        'properties': {
            KEY_DEFAULT_EXPORT_CONFIG: {
                'type': 'string'
            },
            KEY_EXPORT_PATHS: {
                'type': 'array',
                'items': {
                    'type': 'string'
                }
            }
        }
    }
    validator = jsonschema.validators.validator_for(schema)(schema=schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: e.path)
    if errors:
        raise jsonschema.ValidationError(('Configuration File: {}\n'.format(path) + '\n'.join([
            "- '{}' [key path: '{}']".format(error.message, '/'.join([str(p) for p in error.path])) for error in errors
        ])))


class IpubClickConfig(object):
    """ a class to read/write configuration information for the ``click`` CLI"""

    def __init__(self, dir_path=None, file_name=CONFIG_FILENAME):
        self._data = None
        self._dir_path = dir_path or click.get_app_dir(APP_NAME, force_posix=True)
        self._file_path = os.path.join(self._dir_path, CONFIG_FILENAME)

    @property
    def dir_path(self):
        return self._dir_path

    @property
    def file_path(self):
        return self._file_path

    def _load_data(self):
        """ lazy load data, ensuring that all of the config defaults are present """
        import ruamel.yaml as yaml
        if self._data is not None:
            return self._data

        if not os.path.exists(self.file_path):
            return copy.deepcopy(CONFIG_DEFAULTS)

        with io.open(self.file_path) as handle:
            data = yaml.safe_load(handle.read())

        config = copy.deepcopy(CONFIG_DEFAULTS)
        config.update(data)

        validate_config(config, self.file_path)

        self._data = config

        return self._data

    def _save_data(self, data):
        """ save data, ensuring that all of the config defaults are present """
        import ruamel.yaml as yaml
        from ipypublish.utils import create_directory
        config = copy.deepcopy(CONFIG_DEFAULTS)
        config.update(data)
        validate_config(config, self.file_path)
        create_directory(self.dir_path)
        with io.open(self.file_path, 'w') as handle:
            yaml.safe_dump(config, handle)
        self._data = config

    def __getitem__(self, key):
        return copy.deepcopy(self._load_data()[key])

    def __setitem__(self, key, value):
        data = copy.deepcopy(self._load_data())
        data[key] = value
        self._save_data(data)

    @property
    def dict(self):
        return copy.deepcopy(self._load_data())

    def __str__(self):
        import ruamel.yaml as yaml
        data = self._load_data()
        return yaml.safe_dump(data, default_flow_style=False)

    def reset(self):
        self._save_data({})

    @property
    def export_paths(self):
        return self[KEY_EXPORT_PATHS]

    def add_export_path(self, path):
        if not isinstance(path, six.string_types):
            raise TypeError("'{}' is not a string".format(path))
        export_paths = self.export_paths
        if path not in export_paths:
            export_paths.append(path)
        self[KEY_EXPORT_PATHS] = export_paths


pass_config = click.make_pass_decorator(IpubClickConfig, ensure=True)
