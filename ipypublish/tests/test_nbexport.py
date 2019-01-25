import os
import shutil
import tempfile

from ipypublish.main import publish
from ipypublish.scripts import nbexport, nbmerge, pdfexport


def test_nbexport_latex_empty(ipynb1):
    template = ''
    config = {}
    nb, path = nbmerge.merge_notebooks(ipynb1)
    (body, resources), exe = nbexport.export_notebook(
        nb, 'Latex', config, template)
    assert exe == '.tex'
    assert body == ''


def test_nbexport_latex_mkdown1(ipynb1):
    template = """
((* block markdowncell scoped *))
test123
((* endblock markdowncell *))
    """
    config = {}
    nb, path = nbmerge.merge_notebooks(ipynb1)
    (body, resources), exe = nbexport.export_notebook(
        nb, 'Latex', config, template)
    assert exe == '.tex'
    assert body.strip() == 'test123'


def test_nbexport_latex_mkdown2(ipynb1):
    template = """
((*- extends 'display_priority.tplx' -*))
((* block markdowncell scoped *))
(((cell.source)))
((* endblock markdowncell *))
    """
    config = {}
    nb, path = nbmerge.merge_notebooks(ipynb1)
    (body, resources), exe = nbexport.export_notebook(
        nb, 'Latex', config, template)
    assert exe == '.tex'
    assert body.strip() == '# a title\n\nsome text'


def test_nbexport_html_empty(ipynb1):
    template = ''
    config = {}
    nb, path = nbmerge.merge_notebooks(ipynb1)
    (body, resources), exe = nbexport.export_notebook(
        nb, 'HTML', config, template)
    assert exe == '.html'
    assert body == ''


def test_nbexport_html_mkdown1(ipynb1):
    template = """
{% block markdowncell scoped %}
test123
{% endblock markdowncell %}
    """
    config = {}
    nb, path = nbmerge.merge_notebooks(ipynb1)
    (body, resources), exe = nbexport.export_notebook(
        nb, 'HTML', config, template)
    assert exe == '.html'
    assert body.strip() == 'test123'


def test_nbexport_html_mkdown2(ipynb1):
    template = """
{%- extends 'display_priority.tpl' -%}
{% block markdowncell scoped %}
{{cell.source}}
{% endblock markdowncell %}
    """
    config = {}
    nb, path = nbmerge.merge_notebooks(ipynb1)
    (body, resources), exe = nbexport.export_notebook(
        nb, 'HTML', config, template)
    assert exe == '.html'
    assert body.strip() == '# a title\n\nsome text'
