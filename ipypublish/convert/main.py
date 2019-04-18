#!/usr/bin/env python
# import base64
from typing import List, Tuple, Union, Dict  # noqa: F401
import logging
import os
import time
import sys
import inspect

import traitlets as T
from traitlets import default, validate, TraitError
# from traitlets import validate
from traitlets.config.configurable import Configurable
from traitlets.config import Config
from jsonextended import edict
from six import string_types
import jsonschema

import ipypublish
from ipypublish.utils import (pathlib, handle_error,
                              read_file_from_directory,
                              get_module_path,
                              get_valid_filename, find_entry_point)
from ipypublish import schema
from ipypublish.convert.nbmerge import merge_notebooks
from ipypublish.convert.config_manager import (get_export_config_path,
                                               load_export_config,
                                               load_template,
                                               create_exporter_cls)


def dict_to_config(config, unflatten=True, key_as_tuple=False):
    if unflatten:
        config = edict.unflatten(config, key_as_tuple=key_as_tuple, delim=".")
    return Config(config)


class IpyPubMain(Configurable):

    conversion = T.Unicode(
        'latex_ipypublish_main',
        help='key or path to conversion configuration'
    ).tag(config=True)

    plugin_folder_paths = T.Set(
        T.Unicode,
        default_value=(),
        help="a list of folders containing conversion configurations"
    ).tag(config=True)

    @validate("plugin_folder_paths")
    def _validate_plugin_folder_paths(self, proposal):
        folder_paths = proposal['value']
        for path in folder_paths:
            if not os.path.exists(path):
                raise TraitError(
                    "the configuration folder path does not exist: "
                    "{}".format(path))
        return proposal['value']

    outpath = T.Union(
        [T.Unicode(), T.Instance(pathlib.Path)],
        allow_none=True, default_value=None,
        help="path to output converted files"
    ).tag(config=True)

    folder_suffix = T.Unicode(
        "_files",
        help=("suffix for the folder name where content will be dumped "
              "(e.g. internal images). "
              "It will be a sanitized version of the input filename, "
              "followed by the suffix"
              )
    ).tag(config=True)

    ignore_prefix = T.Unicode(
        '_',
        help=("prefixes to ignore, "
              "when finding notebooks to merge")).tag(config=True)

    meta_path_placeholder = T.Unicode(
        "${meta_path}",
        help=("all string values in the export configuration containing "
              "this placeholder will be be replaced with the path to the "
              "notebook from which the metadata was obtained")
    ).tag(config=True)

    files_folder_placeholder = T.Unicode(
        "${files_path}",
        help=("all string values in the export configuration containing "
              "this placeholder will be be replaced with the path "
              "(relative to outpath) to the folder where files will be dumped")
    ).tag(config=True)

    validate_nb_metadata = T.Bool(
        True,
        help=("before running the exporter, validate that "
              "the notebook level metadata is valid again the schema")
    ).tag(config=True)

    pre_conversion_funcs = T.Dict(
        help=("a mapping of file extensions to functions that can convert"
              "that file type Instance(nbformat.NotebookNode) = func(pathstr)")
    ).tag(config=True)

    @default("pre_conversion_funcs")
    def _default_pre_conversion_funcs(self):
        try:
            import jupytext
            return {
                ".Rmd": jupytext.readf
            }
        except ImportError:
            return {}

    @validate("pre_conversion_funcs")
    def _validate_pre_conversion_funcs(self, proposal):
        for ext, func in proposal['value'].items():
            if not ext.startswith("."):
                raise TraitError(
                    "the extension key should start with a '.': "
                    "{}".format(ext))
            try:
                func("string")
                # TODO should do this safely with inspect,
                # but no obvious solution
                # to check if it only requires one string argument
            except TypeError:
                raise TraitError(
                    "the function for {} can not be "
                    "called with a single string arg: "
                    "{}".format(ext, func))
            except Exception:
                pass
        return proposal['value']

    log_to_stdout = T.Bool(
        True,
        help="whether to log to sys.stdout"
    ).tag(config=True)

    log_level_stdout = T.Enum(
        ['debug', 'info', 'warning', 'error',
         'DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default_value='INFO',
        help='the logging level to output to stdout'
    ).tag(config=True)

    log_stdout_formatstr = T.Unicode(
        '%(levelname)s:%(name)s:%(message)s'
    ).tag(config=True)

    log_to_file = T.Bool(
        False,
        help="whether to log to file"
    ).tag(config=True)

    log_level_file = T.Enum(
        ['debug', 'info', 'warning', 'error',
         'DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default_value='INFO',
        help='the logging level to output to file'
    ).tag(config=True)

    log_file_path = T.Unicode(
        None,
        allow_none=True,
        help="if None, will output to {outdir}/{ipynb_name}.nbpub.log"
    ).tag(config=True)

    log_file_formatstr = T.Unicode(
        '%(levelname)s:%(name)s:%(message)s'
    ).tag(config=True)

    default_ppconfig_kwargs = T.Dict(
        trait=T.Bool(),
        default_value=(
            ('pdf_in_temp', False),
            ('pdf_debug', False),
            ('launch_browser', False)),
        help=("convenience arguments for constructing the post-processors "
              "default configuration")
    ).tag(config=True)

    default_pporder_kwargs = T.Dict(
        trait=T.Bool(),
        default_value=(
            ('dry_run', False),
            ('clear_existing', False),
            ('dump_files', False),
            ('create_pdf', False),
            ('serve_html', False),
            ('slides', False)),
        help=("convenience arguments for constructing the post-processors "
              "default list")
    ).tag(config=True)

    # TODO validate that default_ppconfig/pporder_kwargs can be parsed to funcs

    default_exporter_config = T.Dict(
        help="default configuration for exporters"
    ).tag(config=True)

    @default('default_exporter_config')
    def _default_exporter_config(self):
        temp = '${files_path}/{unique_key}_{cell_index}_{index}{extension}'
        return {'ExtractOutputPreprocessor': {
            'output_filename_template': temp}}

    def _create_default_ppconfig(self, pdf_in_temp=False, pdf_debug=False,
                                 launch_browser=False):
        """create a default config for postprocessors"""
        return Config({
            "PDFExport": {
                "files_folder": "${files_path}",
                "convert_in_temp": pdf_in_temp,
                "debug_mode": pdf_debug,
                "open_in_browser": launch_browser,
                "skip_mime": False
            },
            "RunSphinx": {
                "open_in_browser": launch_browser,
            },
            "RemoveFolder": {
                "files_folder": "${files_path}"
            },
            "CopyResourcePaths": {
                "files_folder": "${files_path}"
            },
            "ConvertBibGloss": {
                "files_folder": "${files_path}"
            }
        })

    def _create_default_pporder(self, dry_run=False, clear_existing=False,
                                dump_files=False, create_pdf=False,
                                serve_html=False, slides=False):
        """create a default list of postprocessors to run"""
        default_pprocs = [
            'remove-blank-lines',
            'remove-trailing-space',
            'filter-output-files']
        if slides:
            default_pprocs.append('fix-slide-refs')
        if not dry_run:
            if clear_existing:
                default_pprocs.append('remove-folder')
            default_pprocs.append('write-text-file')
            if dump_files or create_pdf or serve_html:
                default_pprocs.extend(
                    [
                        'write-resource-files',
                        'copy-resource-paths',
                        'convert-bibgloss'])
            if create_pdf:
                default_pprocs.append('pdf-export')
            elif serve_html:
                default_pprocs.append('reveal-server')

        return default_pprocs

    @property
    def logger(self):
        return logging.getLogger("ipypublish")

    def _setup_logger(self, ipynb_name, outdir):

        root = logging.getLogger()

        if self.log_to_stdout or self.log_to_file:
            # remove any existing handlers
            root.handlers = []
            root.setLevel(logging.DEBUG)

        if self.log_to_stdout:
            # setup logging to terminal
            slogger = logging.StreamHandler(sys.stdout)
            slogger.setLevel(getattr(logging, self.log_level_stdout.upper()))
            formatter = logging.Formatter(self.log_stdout_formatstr)
            slogger.setFormatter(formatter)
            slogger.propogate = False
            root.addHandler(slogger)

        if self.log_to_file:
            # setup logging to file
            if self.log_file_path:
                path = self.log_file_path
            else:
                path = os.path.join(outdir, ipynb_name + '.nbpub.log')

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            flogger = logging.FileHandler(path, 'w')
            flogger.setLevel(getattr(logging, self.log_level_file.upper()))
            formatter = logging.Formatter(self.log_file_formatstr)
            flogger.setFormatter(formatter)
            flogger.propogate = False
            root.addHandler(flogger)

    def __init__(self, config=None):
        """
        Public constructor

        Parameters
        ----------
        config: traitlets.config.Config
            User configuration instance.

        """
        # with_default_config = self.default_config
        # if config:
        #     with_default_config.merge(config)
        if config is None:
            config = {}
        if not isinstance(config, Config):
            config = Config(config)
        with_default_config = config

        super(IpyPubMain, self).__init__(config=with_default_config)

    def __call__(self, ipynb_path, nb_node=None):
        """see IpyPubMain.publish"""
        return self.publish(ipynb_path, nb_node)

    def publish(self, ipynb_path, nb_node=None):
        """ convert one or more Jupyter notebooks to a published format

        paths can be string of an existing file or folder,
        or a pathlib.Path like object

        all files linked in the documents are placed into a single files_folder

        Parameters
        ----------
        ipynb_path: str or pathlib.Path
            notebook file or directory
        nb_node: None or nbformat.NotebookNode
            a pre-converted notebook

        Returns
        --------
        outdata: dict
            containing keys;
            "outpath", "exporter", "stream", "main_filepath", "resources"

        """
        # setup the input and output paths
        if isinstance(ipynb_path, string_types):
            ipynb_path = pathlib.Path(ipynb_path)
        ipynb_name, ipynb_ext = os.path.splitext(ipynb_path.name)
        outdir = (os.path.join(os.getcwd(), 'converted')
                  if self.outpath is None else str(self.outpath))

        self._setup_logger(ipynb_name, outdir)

        if not ipynb_path.exists() and not nb_node:
            handle_error('the notebook path does not exist: {}'.format(
                ipynb_path), IOError, self.logger)

        # log start of conversion
        self.logger.info('started ipypublish v{0} at {1}'.format(
            ipypublish.__version__, time.strftime("%c")))
        self.logger.info('logging to: {}'.format(
            os.path.join(outdir, ipynb_name + '.nbpub.log')))
        self.logger.info('running for ipynb(s) at: {0}'.format(ipynb_path))
        self.logger.info(
            'with conversion configuration: {0}'.format(self.conversion))

        if nb_node is None and ipynb_ext in self.pre_conversion_funcs:
            func = self.pre_conversion_funcs[ipynb_ext]
            self.logger.info(
                "running pre-conversion with: {}".format(
                    inspect.getmodule(func)))
            try:
                nb_node = func(ipynb_path)
            except Exception as err:
                handle_error(
                    "pre-conversion failed for {}: {}".format(ipynb_path, err),
                    err, self.logger)

        # doesn't work with folders
        # if (ipynb_ext != ".ipynb" and nb_node is None):
        #     handle_error(
        #         'the file extension is not associated with any '
        #         'pre-converter: {}'.format(ipynb_ext),
        # TypeError, self.logger)

        if nb_node is None:
            # merge all notebooks
            # TODO allow notebooks to remain separate
            # (would require creating a main.tex with the preamble in etc )
            # Could make everything a 'PyProcess',
            # with support for multiple streams
            final_nb, meta_path = merge_notebooks(
                ipynb_path, ignore_prefix=self.ignore_prefix)
        else:
            final_nb, meta_path = (nb_node, ipynb_path)

        # valdate the notebook metadata against the schema
        if self.validate_nb_metadata:
            nb_metadata_schema = read_file_from_directory(
                get_module_path(schema), "doc_metadata.schema.json",
                "doc_metadata.schema", self.logger, interp_ext=True)
            try:
                jsonschema.validate(final_nb.metadata, nb_metadata_schema)
            except jsonschema.ValidationError as err:
                handle_error(
                    "validation of notebook level metadata failed: {}\n"
                    "see the doc_metadata.schema.json for full spec".format(
                        err.message),
                    jsonschema.ValidationError, logger=self.logger)

        # set text replacements for export configuration
        replacements = {
            self.meta_path_placeholder: str(meta_path),
            self.files_folder_placeholder: "{}{}".format(
                get_valid_filename(ipynb_name), self.folder_suffix)
        }

        self.logger.debug('notebooks meta path: {}'.format(meta_path))

        # load configuration file
        (exporter_cls, jinja_template,
         econfig, pprocs, pconfig) = self._load_config_file(replacements)

        # run nbconvert
        self.logger.info('running nbconvert')
        exporter, stream, resources = self.export_notebook(
            final_nb, exporter_cls, econfig, jinja_template)

        # postprocess results
        main_filepath = os.path.join(
            outdir, ipynb_name + exporter.file_extension)

        for post_proc_name in pprocs:
            proc_class = find_entry_point(
                post_proc_name, "ipypublish.postprocessors",
                self.logger, "ipypublish")
            proc = proc_class(pconfig)
            stream, main_filepath, resources = proc.postprocess(
                stream, exporter.output_mimetype, main_filepath,
                resources)

        self.logger.info('process finished successfully')

        return {
            "outpath": outdir,
            "exporter": exporter,
            "stream": stream,
            "main_filepath": main_filepath,
            "resources": resources
        }

    def _load_config_file(self, replacements):
        # find conversion configuration
        self.logger.info(
            'finding conversion configuration: {}'.format(self.conversion))
        export_config_path = None
        if isinstance(self.conversion, string_types):
            outformat_path = pathlib.Path(self.conversion)
        else:
            outformat_path = self.conversion
        if outformat_path.exists():  # TODO use pathlib approach
            # if is outformat is a path that exists, use that
            export_config_path = outformat_path
        else:
            # else search internally
            export_config_path = get_export_config_path(
                self.conversion, self.plugin_folder_paths)

        if export_config_path is None:
            handle_error(
                "could not find conversion configuration: {}".format(
                    self.conversion),
                IOError, self.logger)

        # read conversion configuration and create
        self.logger.info('loading conversion configuration')
        data = load_export_config(export_config_path)
        self.logger.info('creating exporter')
        exporter_cls = create_exporter_cls(data["exporter"]["class"])
        self.logger.info('creating template and loading filters')
        template_name = "template_file"
        jinja_template = load_template(template_name, data["template"])
        self.logger.info('creating process configuration')
        export_config = self._create_export_config(
            data["exporter"], template_name, replacements)
        pprocs, pproc_config = self._create_pproc_config(
            data.get("postprocessors", {}), replacements)

        return (exporter_cls, jinja_template,
                export_config, pprocs, pproc_config)

    def _create_export_config(self, exporter_data,
                              template_name, replacements):
        # type: (dict, Dict[str, str]) -> Config
        config = {}
        exporter_name = exporter_data["class"].split(".")[-1]

        config[exporter_name + ".template_file"] = template_name
        config[exporter_name + ".filters"] = exporter_data.get("filters", [])

        preprocessors = []
        for preproc in exporter_data.get("preprocessors", []):
            preprocessors.append(preproc["class"])
            preproc_name = preproc["class"].split(".")[-1]
            for name, val in preproc.get("args", {}).items():
                config[preproc_name + "." + name] = val

        config[exporter_name + ".preprocessors"] = preprocessors

        for name, val in exporter_data.get("other_args", {}).items():
            config[name] = val

        final_config = self.default_exporter_config
        final_config.update(config)

        replace_placeholders(final_config, replacements)

        return dict_to_config(final_config, True)

    def _create_pproc_config(self, pproc_data, replacements):

        if "order" in pproc_data:
            pprocs_list = pproc_data["order"]
        else:
            pprocs_list = self._create_default_pporder(
                **self.default_pporder_kwargs)

        pproc_config = self._create_default_ppconfig(
            **self.default_ppconfig_kwargs)

        if "config" in pproc_data:
            override_config = pproc_data["config"]
            pproc_config.update(override_config)

        replace_placeholders(pproc_config, replacements)

        return pprocs_list, pproc_config

    def export_notebook(self, final_nb, exporter_cls, config, jinja_template):

        kwargs = {"config": config}
        if jinja_template is not None:
            kwargs["extra_loaders"] = [jinja_template]
        try:
            exporter = exporter_cls(**kwargs)
        except TypeError:
            self.logger.warning(
                "the exporter class can not be parsed "
                "the arguments: {}".format(list(kwargs.keys())))
            exporter = exporter_cls()

        body, resources = exporter.from_notebook_node(final_nb)
        return exporter, body, resources


def replace_placeholders(mapping, replacements):
    """ recurse through a mapping and perform (in-place) string replacements

    Parameters
    ----------
    mapping:
        any object which has an items() attribute
    replacements: dict
        {placeholder: replacement}

    """
    for key, val in mapping.items():
        if isinstance(val, string_types):
            for instr, outstr in replacements.items():
                val = val.replace(instr, outstr)
            mapping[key] = val
        elif hasattr(val, "items"):
            replace_placeholders(val, replacements)
