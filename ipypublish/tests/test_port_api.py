import os
import json
from ipypublish.port_api.plugin_to_json import convert_to_json
from ipypublish.port_api.tpl_dct_to_json import py_to_json
from ipypublish.port_api.convert_format_str import convert_format_str
from ipypublish.tests import TEST_FILES_DIR


def test_plugin_to_json_html():

    out_str = convert_to_json(os.path.join(TEST_FILES_DIR, 'port_api_files',
                                           "html_ipypublish_all.py.txt"))
    dct = json.loads(out_str)
    assert "exporter" in dct  # TODO test against schema


def test_plugin_to_json_latex():

    out_str = convert_to_json(os.path.join(TEST_FILES_DIR, 'port_api_files',
                                           "latex_ipypublish_all.py.txt"))
    dct = json.loads(out_str)
    assert "exporter" in dct  # TODO test against schema


def test_py_to_json():

    out_str = py_to_json(os.path.join(TEST_FILES_DIR, 'port_api_files',
                                      "front_pages.py.txt"))
    dct = json.loads(out_str)
    assert "segments" in dct  # TODO test against schema


def test_convert_format_str():

    template = ["{{%- extends 'null.tpl' -%}}",
                "{{% block header %}}",
                "{{{{ nb.metadata | meta2yaml('#~~ ') }}}}",
                "{{% endblock header %}}",
                "{{% block codecell %}}",
                "#%%",
                "{{{{ super() }}}}",
                "{{% endblock codecell %}}",
                "{{% block in_prompt %}}{{% endblock in_prompt %}}",
                "{{% block input %}}{{{{ cell.metadata | meta2yaml('#~~ ') }}}}",  # noqa: E501
                "{{{{ cell.source | ipython2python }}}}",
                "{{% endblock input %}}",
                "{{% block markdowncell scoped %}}#%% [markdown]",
                "{{{{ cell.metadata | meta2yaml('#~~ ') }}}}",
                "{{{{ cell.source | comment_lines }}}}",
                "{{% endblock markdowncell %}}"
                ]

    convert_format_str(template)
