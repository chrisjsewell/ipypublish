#!/usr/bin/env python

"""
create template

philosophy is only turn stuff on when we want

http://nbconvert.readthedocs.io/en/latest/customizing.html#Template-structure
http://nbconvert.readthedocs.io/en/latest/api/exporters.html#nbconvert.exporters.TemplateExporter

"""
from typing import List, Tuple, Union  # noqa: F401
import logging
import jsonschema
# from ipypublish import __version__


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
    segment_datas: tuple of dict
    outpath: 
        if not None, output to path

    """
    # TODO validate outline schema
    # get outline info
    outline_content = "\n".join(outline_schema.get("outline"))
    placeholders = outline_schema["properties"]["segments"]["properties"]

    replacements = {key: "" for key in placeholders.keys()}
    docstrings = [
        outline_schema.get("$id"),
        outline_schema.get("description"),
        "with segments:"
    ]

    for segment_data in segment_datas:
        # validate segment against outline schema
        jsonschema.validate(segment_data, outline_schema)
        # TODO better validation error output for user

        # get description of segment
        docstrings.append(
            "- {0}: {1}".format(
                segment_data["identifier"], segment_data["description"])
        )

        # find what key to overwrite
        overwrite = segment_data.get("overwrite", [])
        logging.debug('overwrite keys: {}'.format(overwrite))

        for key, val in segment_data.get("segments").items():
            valstring = "\n".join(val)
            if key in overwrite:
                replacements[key] = valstring
            elif 'append_before' in placeholders[key]["$ref"]:
                replacements[key] = valstring + '\n' + replacements[key]
            elif 'append_after' in placeholders[key]["$ref"]:
                replacements[key] = replacements[key] + '\n' + valstring
            else:
                raise jsonschema.ValidationError(
                    "properties/segments/properties/{0}/$ref ".format(key) +
                    "should contain either append_before or append_before")

    replacements["meta_docstring"] = "\n".join(docstrings).replace("'", '"')
    # TODO add option to include ipypub version in output file
    # not included by default,
    # since it would require the test files to be updated with every version
    replacements["ipypub_version"] = ""  # str(__version__)

    outline = outline_content.format(**replacements)

    if outpath is not None:
        with open(outpath, 'w') as f:  # TODO use pathlib
            f.write(outline)
        return

    return outline
