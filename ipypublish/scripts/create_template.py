#!/usr/bin/env python
"""
create template

philosophy is only turn stuff on when we want

http://nbconvert.readthedocs.io/en/latest/customizing.html#Template-structure
http://nbconvert.readthedocs.io/en/latest/api/exporters.html#nbconvert.exporters.TemplateExporter

"""
from typing import List, Tuple, Union  # noqa: F401
import re
import logging
import jsonschema

# from ipypublish import __version__
from ipypublish.utils import (read_file_from_module,
                              read_file_from_directory,
                              handle_error)

logger = logging.getLogger(__name__)


def multireplace(string, replacements):
    """
    Given a string and a replacement map, it returns the replaced string.

    From https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729

    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
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


def create_template(outline_schema, segment_datas, outpath=None):
    # type: (dict, Tuple[dict]) -> str
    """ build a latex jinja template from;

    - a json file, defining a jinja template outline,
      containing segment placeholders, and a schema for segments,
    - and json segment files adhering to the schema

    if a segment contains the key "overwrite",
    then its value should be a list of keys,
    such that these key values overwrite any entries before

    Parameters
    ----------
    outline_schema: dict
    segment_datas: tuple or dict
    outpath:  None or str
        if not None, output to path

    """
    # TODO validate outline schema

    # get jinja template
    if "directory" in outline_schema["outline"]:
        outline_content = read_file_from_directory(
            outline_schema["outline"]["directory"],
            outline_schema["outline"]["file"], "template outline", logger)
    else:
        outline_content = read_file_from_module(
            outline_schema["outline"]["module"],
            outline_schema["outline"]["file"], "template outline", logger)

    # get the placeholders @ipubreplace{above|below}{name}
    regex = re.compile("@ipubreplace{(.+)}{(.+)}", re.MULTILINE)
    placeholder_tuple = regex.findall(outline_content)
    placeholders = {name: append for append, name in placeholder_tuple}

    replacements = {key: "" for key in placeholders.keys()}
    docstrings = [
        outline_schema.get("$id"),
        outline_schema.get("description"),
        "with segments:"
    ]

    for seg_num, segment_data in enumerate(segment_datas):

        # validate segment against outline schema
        try:
            jsonschema.validate(segment_data, outline_schema)
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

        for key, val in segment_data.get("segments").items():
            valstring = "\n".join(val)
            if key in overwrite:
                replacements[key] = valstring
            elif placeholders[key] == "above":
                replacements[key] = valstring + '\n' + replacements[key]
            elif placeholders[key] == "below":
                replacements[key] = replacements[key] + '\n' + valstring
            else:
                # TODO this should be part of the schema?
                handle_error((
                    "the placeholder @ipubreplace{{{0}}}{{{1}}} ".format(
                        key, placeholders[key]) +
                    "should specify above or below appending"),
                    jsonschema.ValidationError, logger=logger)

    if "meta_docstring" in placeholders:
        docstring = "\n".join(docstrings).replace("'", '"')
        replacements["meta_docstring"] = docstring
    if "ipypub_version" in placeholders:
        # TODO add option to include ipypub version in output file
        # not included by default,
        # since tests need to be changed to ignore version number
        replacements["ipypub_version"] = ""  # str(__version__)

    replace_dict = {
        "@ipubreplace{{{0}}}{{{1}}}".format(append, name): replacements[name]
        for append, name in placeholder_tuple}
    outline = multireplace(outline_content, replace_dict)

    if outpath is not None:
        with open(outpath, 'w') as f:  # TODO use pathlib
            f.write(outline)
        return

    return outline
