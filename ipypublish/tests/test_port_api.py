import os
import json
from ipypublish.port_api.plugin_to_json import convert_to_json
from ipypublish.port_api.tpl_dct_to_json import py_to_json
from ipypublish.tests import TEST_FILES_DIR


def test_plugin_to_json_html():

    out_str = convert_to_json(os.path.join(TEST_FILES_DIR,
                                           "html_ipypublish_all.py.txt"))
    dct = json.loads(out_str)
    assert "exporter" in dct  # TODO test against schema


def test_plugin_to_json_latex():

    out_str = convert_to_json(os.path.join(TEST_FILES_DIR,
                                           "latex_ipypublish_all.py.txt"))
    dct = json.loads(out_str)
    assert "exporter" in dct  # TODO test against schema


def test_py_to_json():

    out_str = py_to_json(os.path.join(TEST_FILES_DIR,
                                      "front_pages.py.txt"))
    dct = json.loads(out_str)
    assert "segments" in dct  # TODO test against schema