import copy
import io
import os

import click

APP_NAME = 'IpyPublish'
CONFIG_FILENAME = '.ipypub_config.yaml'


class IpubClickConfig(object):
    """ a class to read/write configuration information for the ``click`` CLI"""
    _export_paths_key = 'export_paths'

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
        """ lazy load data """
        import ruamel.yaml as yaml
        if self._data is not None:
            return self._data

        if not os.path.exists(self.file_path):
            return {}

        with io.open(self.file_path) as handle:
            self._data = yaml.safe_load(handle.read())
        return self._data

    @property
    def dict(self):
        return copy.deepcopy(self._load_data())

    def __str__(self):
        import ruamel.yaml as yaml
        data = self._load_data()
        return yaml.safe_dump(data, default_flow_style=False)

    def _save_data(self, data):
        import ruamel.yaml as yaml
        from ipypublish.utils import create_directory
        create_directory(self.dir_path)
        with io.open(self.file_path, 'w') as handle:
            yaml.safe_dump(data, handle)

    def _set_key(self, key, value):
        data = self._load_data()
        data[key] = value
        self._save_data(data)

    def reset(self):
        self._save_data({})

    @property
    def export_paths(self):
        return self._load_data().get(self._export_paths_key, [])

    def add_export_path(self, path):
        export_paths = self.export_paths
        if path not in export_paths:
            export_paths.append(path)
        self._set_key(self._export_paths_key, export_paths)


pass_config = click.make_pass_decorator(IpubClickConfig, ensure=True)
