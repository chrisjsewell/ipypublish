#!/usr/bin/env python
"""
create template

philosophy is only turn stuff on when we want

http://nbconvert.readthedocs.io/en/latest/customizing.html#Template-structure
http://nbconvert.readthedocs.io/en/latest/api/exporters.html#nbconvert.exporters.TemplateExporter

"""
from typing import List, Tuple, Union  # noqa: F401
import re
import io
import logging
import jsonschema

from six import string_types

# from ipypublish import __version__
from ipypublish import schema
from ipypublish.utils import (handle_error,
                              read_file_from_directory, get_module_path)

logger = logging.getLogger("template")

_SEGMENT_SCHEMA_FILE = "segment.schema.json"
_SEGMENT_SCHEMA = None


def multireplace(string, replacements):
    """
    Given a string and a replacement map, it returns the replaced string.

    From https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729

    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {find value: replacement}
    :rtype: str

    """
    if not replacements:
        return string

    # Place longer ones first to keep shorter substrings from matching,
    # where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'}
    # against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    substrs = sorted(replacements, key=len, reverse=True)

    # Create a big OR regex that matches any of the substrings to replace
    regexp = re.compile('|'.join(map(re.escape, substrs)))

    # For each match, look up the new string in the replacements
    return regexp.sub(lambda match: replacements[match.group(0)], string)


def _output_to_file(content, outpath):
    if outpath is not None:
        with io.open(outpath, "w", encoding='utf8') as f:  # TODO use pathlib
            f.write(content)
        return


def create_template(outline_template, outline_name,
                    segment_datas,
                    outpath=None):
    # type: (dict, Tuple[dict]) -> str
    """ build a latex jinja template from;

    - a jinja(2) template outline,
      which may contain segment placeholders,
    - and json segment files adhering to the segment.schema.json schema

    if a segment contains the key "overwrite",
    then its value should be a list of keys,
    such that these key values overwrite any entries before

    Parameters
    ----------
    outline_template: str
    segment_datas: tuple or dict
    outpath:  None or str
        if not None, output to path

    """
    # get the placeholders @ipubreplace{above|below}{name}
    regex = re.compile("\\@ipubreplace\\{([^\\}]+)\\}\\{([^\\}]+)\\}",
                       re.MULTILINE)
    placeholder_tuple = regex.findall(outline_template)

    if not placeholder_tuple:
        if segment_datas:
            handle_error(
                "the segment data is provided, " +
                "but the outline template contains no placeholders",
                KeyError, logger)

        if outpath:
            _output_to_file(outline_template, outpath)
        return outline_template

    placeholders = {name: append for append, name in placeholder_tuple}
    # TODO validate that placeholders to not exist multiple times,
    # with above and below

    replacements = {key: "" for key in placeholders.keys()}
    docstrings = [
        "outline: {}".format(outline_name),
    ]

    if segment_datas:
        docstrings.append("with segments:")
        global _SEGMENT_SCHEMA
        if _SEGMENT_SCHEMA is None:
            # lazy segment schema once
            _SEGMENT_SCHEMA = read_file_from_directory(
                get_module_path(schema),
                _SEGMENT_SCHEMA_FILE,
                "segment configuration schema", logger, interp_ext=True)

    for seg_num, segment_data in enumerate(segment_datas):

        # validate segment
        try:
            jsonschema.validate(segment_data, _SEGMENT_SCHEMA)
        except jsonschema.ValidationError as err:
            handle_error(
                "validation of template segment {} failed: {}".format(
                    seg_num, err.message),
                jsonschema.ValidationError, logger=logger)

        # get description of segment
        docstrings.append(
            "- {0}: {1}".format(
                segment_data["identifier"], segment_data["description"])
        )

        # find what key to overwrite
        overwrite = segment_data.get("overwrite", [])
        logger.debug('overwrite keys: {}'.format(overwrite))

        for key, segtext in segment_data.get("segments").items():

            if key not in placeholders:
                handle_error(
                    "the segment key '{}' ".format(key) +
                    "is not contained in the outline template",
                    KeyError, logger)

            if not isinstance(segtext, string_types):
                segtext = "\n".join(segtext)
            if key in overwrite:
                replacements[key] = segtext
            elif placeholders[key] == "above":
                replacements[key] = segtext + '\n' + replacements[key]
            elif placeholders[key] == "below":
                replacements[key] = replacements[key] + '\n' + segtext
            else:
                handle_error((
                    "the placeholder @ipubreplace{{{0}}}{{{1}}} ".format(
                        key, placeholders[key]) +
                    "should specify 'above' or 'below' appending"),
                    jsonschema.ValidationError, logger=logger)

    if "meta_docstring" in placeholders:
        docstring = "\n".join([s for s in docstrings if s]).replace("'", '"')
        replacements["meta_docstring"] = docstring
    if "ipypub_version" in placeholders:
        # TODO add option to include ipypub version in output file
        # not included by default,
        # since tests need to be changed to ignore version number
        replacements["ipypub_version"] = ""  # str(__version__)

    prefix = "@ipubreplace{"
    replace_dict = {
        prefix + append + "}{" + name + "}": replacements.get(
            name, "")
        for append, name in placeholder_tuple}
    outline = multireplace(outline_template, replace_dict)

    if outpath:
        _output_to_file(outline, outpath)

    return outline
