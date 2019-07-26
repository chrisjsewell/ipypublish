# import difflib  # TODO
import fnmatch
import glob
import importlib
import logging
import os

from jinja2 import DictLoader
import jsonschema
import nbconvert  # noqa: F401
import importlib_resources

from ipypublish.utils import (handle_error, ResourceFile)
from ipypublish import export_plugins
from ipypublish import schema
from ipypublish.templates.create_template import create_template

_TEMPLATE_KEY = 'new_template'
_EXPORT_SCHEMA_FILE = 'export_config.schema.json'
_EXPORT_SCHEMA = None

logger = logging.getLogger('configuration')


def get_export_config_file(export_key, config_folder_paths=(), find_closest_matches=1, match_cutoff=0.5):
    # type (string, Tuple[str]) -> (Union[string, None], Union[string, None])
    """we search for a plugin name, which matches the supplied plugin name
    """
    if os.path.exists(export_key):
        return ResourceFile(export_key, description='export plugin')

    names = []
    for config in iter_all_export_files(config_folder_paths):
        if config.name == export_key:
            return config
        if find_closest_matches is not None:
            names.append(config.name)

    # if find_closest_matches is not None:
    #     difflib.get_close_matches(export_key, names, n=find_closest_matches, cutoff=match_cutoff)
    return None


def iter_all_export_files(config_folder_paths=(), regex='*.json'):
    """we iterate through all json files in the
    supplied plugin_folder_paths, and then in the `export_plugins` folder
    """
    for entry in importlib_resources.contents(export_plugins):
        if fnmatch.fnmatch(entry, regex):
            yield ResourceFile(entry, export_plugins, description='export plugin')

    for plugin_folder_path in config_folder_paths:
        for jsonpath in glob.glob(os.path.join(plugin_folder_path, regex)):
            yield ResourceFile(jsonpath, description='export plugin')


def load_export_config(export_config_file):
    """load the export configuration"""
    data = export_config_file.get_data(logger)

    # validate against schema
    global _EXPORT_SCHEMA
    if _EXPORT_SCHEMA is None:
        # lazy load schema once
        resource = ResourceFile(_EXPORT_SCHEMA_FILE, resource_module=schema, description='export configuration schema')
        _EXPORT_SCHEMA = resource.get_data(logger)

    try:
        jsonschema.validate(data, _EXPORT_SCHEMA)
    except jsonschema.ValidationError as err:
        handle_error(
            msg='validation of export config {} failed against {}'.format(export_config_file, _EXPORT_SCHEMA_FILE),
            exception=err,
            logger=logger)

    return data


def iter_all_export_infos(config_folder_paths=(), regex='*.json', get_mime=False):
    """iterate through all export configuration and yield a dict of info"""
    for export_file in iter_all_export_files(config_folder_paths, regex):
        data = load_export_config(export_file)

        info = dict([('key', export_file.name), ('class', data['exporter']['class']), ('path', str(export_file)),
                     ('description', data['description'])])

        if get_mime:
            info['mime_type'] = create_exporter_cls(data['exporter']['class']).output_mimetype

        yield info


def get_plugin_str(plugin_folder_paths=(), regex=None, verbose=False):
    """return string listing all available export configurations """
    outstrs = []
    # outstrs.append('Available Export Configurations')
    # outstrs.append('-------------------------------')
    configs = [
        e for e in iter_all_export_infos(plugin_folder_paths, get_mime=verbose)
        if regex is None or fnmatch.fnmatch(e['key'], '*{}*'.format(regex))
    ]

    for item in sorted(configs, key=lambda i: (i['class'], i['key'])):
        outstrs.append('- Key:   {}'.format(item['key']))
        outstrs.append('  Class: {}'.format(item['class']))
        path = item['path'].split(os.path.sep)
        if verbose:
            outstrs.append('  Type:  {}'.format(item['mime_type']))
        if verbose or len(path) < 3:
            path = os.path.join(*path)
        else:
            path = os.path.join('...', *path[-3:])

        if len(path) < 4:
            outstrs.append('  Path:  {}'.format(item['path']))
        else:
            outstrs.append('  Path:  {}'.format(path))

        outstrs.append('  About: {}'.format(item['description'][0].strip()))
        if verbose:
            for descript in item['description'][1:]:
                outstrs.append('         {}'.format(descript.strip()))
        # note could wrap description (less than x characters)
        outstrs.append(' ')

    return '\n'.join(outstrs)


def create_exporter_cls(class_str):
    # type: (str) -> nbconvert.exporters.Exporter
    """dynamically load export class"""
    export_class_path = class_str.split('.')
    module_path = '.'.join(export_class_path[0:-1])
    class_name = export_class_path[-1]
    try:
        export_module = importlib.import_module(module_path)
    except ModuleNotFoundError as err:
        handle_error(
            msg='module {} containing exporter class {} not found'.format(module_path, class_name),
            exception=err,
            logger=logger)
    if hasattr(export_module, class_name):
        export_class = getattr(export_module, class_name)
    else:
        handle_error(
            msg='module {} does not contain class {}'.format(module_path, class_name), klass=ImportError, logger=logger)

    return export_class


def get_export_extension(export_config_path):
    """return the file extension of the exporter class"""
    data = load_export_config(export_config_path)
    exporter_cls = create_exporter_cls(data['exporter']['class'])
    return exporter_cls.file_extension


def str_to_jinja(template_str, template_key='jinja_template'):
    return DictLoader({template_key: template_str})


def load_template(template_key, template_dict):

    if template_dict is None:
        return None

    if 'directory' in template_dict['outline']:
        resource = ResourceFile(
            os.path.join(template_dict['outline']['directory'], template_dict['outline']['file']),
            description='template outline')
        outline_template = resource.get_text(logger)
        outline_name = os.path.join(template_dict['outline']['directory'], template_dict['outline']['file'])
    else:
        resource = ResourceFile(
            template_dict['outline']['file'],
            resource_module=template_dict['outline']['module'],
            description='template outline')
        outline_template = resource.get_text(logger)
        outline_name = os.path.join(template_dict['outline']['module'], template_dict['outline']['file'])

    segments = []
    for snum, segment in enumerate(template_dict.get('segments', [])):

        if 'file' not in segment:
            handle_error(masg="'file' expected in segment {}".format(snum), klass=KeyError, logger=logger)

        if 'directory' in segment:
            resource = ResourceFile(os.path.join(segment['directory'], segment['file']), description='template segment')
            outline_template = resource.get_data(logger)
        elif 'module' in segment:
            resource = ResourceFile(segment['file'], resource_module=segment['module'], description='template segment')
            seg_data = resource.get_data(logger)
        else:
            handle_error(
                msg="'directory' or 'module' expected in segment {}".format(snum), klass=KeyError, logger=logger)

        segments.append(seg_data)

    template_str = create_template(outline_template, outline_name, segments)

    return str_to_jinja(template_str, template_key)
