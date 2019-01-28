from ipypublish.scripts import nbmerge
from ipypublish.convert.config_manager import (
    create_exporter_cls, str_to_jinja
)
from ipypublish.convert.main import (dict_to_config, export_notebook)


def test_nbexport_latex_empty(ipynb1):
    template = str_to_jinja('')
    config = dict_to_config({})
    exporter_cls = create_exporter_cls('nbconvert.exporters.LatexExporter')
    nb, path = nbmerge.merge_notebooks(ipynb1)
    exporter, body, resources = export_notebook(nb, exporter_cls,
                                                config, template)
    assert exporter.output_mimetype == 'text/latex'
    assert body == ''


def test_nbexport_latex_mkdown1(ipynb1):
    template = str_to_jinja("""
((* block markdowncell scoped *))
test123
((* endblock markdowncell *))
    """)
    config = dict_to_config({})
    nb, path = nbmerge.merge_notebooks(ipynb1)
    exporter_cls = create_exporter_cls('nbconvert.exporters.LatexExporter')
    exporter, body, resources = export_notebook(nb, exporter_cls,
                                                config, template)
    assert exporter.output_mimetype == 'text/latex'
    assert body.strip() == 'test123'


def test_nbexport_latex_mkdown2(ipynb1):
    template = str_to_jinja("""
((*- extends 'display_priority.tplx' -*))
((* block markdowncell scoped *))
(((cell.source)))
((* endblock markdowncell *))
    """)
    config = dict_to_config({})
    nb, path = nbmerge.merge_notebooks(ipynb1)
    exporter_cls = create_exporter_cls('nbconvert.exporters.LatexExporter')
    exporter, body, resources = export_notebook(nb, exporter_cls,
                                                config, template)
    assert exporter.output_mimetype == 'text/latex'

    assert body.strip() == '# a title\n\nsome text'


def test_nbexport_html_empty(ipynb1):
    template = str_to_jinja('')
    config = dict_to_config({})
    nb, path = nbmerge.merge_notebooks(ipynb1)
    exporter_cls = create_exporter_cls('nbconvert.exporters.HTMLExporter')
    exporter, body, resources = export_notebook(nb, exporter_cls,
                                                config, template)
    assert exporter.output_mimetype == 'text/html'

    assert body == ''


def test_nbexport_html_mkdown1(ipynb1):
    template = str_to_jinja("""
{% block markdowncell scoped %}
test123
{% endblock markdowncell %}
    """)
    config = dict_to_config({})
    nb, path = nbmerge.merge_notebooks(ipynb1)
    exporter_cls = create_exporter_cls('nbconvert.exporters.HTMLExporter')
    exporter, body, resources = export_notebook(nb, exporter_cls,
                                                config, template)
    assert exporter.output_mimetype == 'text/html'

    assert body.strip() == 'test123'


def test_nbexport_html_mkdown2(ipynb1):
    template = str_to_jinja("""
{%- extends 'display_priority.tpl' -%}
{% block markdowncell scoped %}
{{cell.source}}
{% endblock markdowncell %}
    """)
    config = dict_to_config({})
    nb, path = nbmerge.merge_notebooks(ipynb1)
    exporter_cls = create_exporter_cls('nbconvert.exporters.HTMLExporter')
    exporter, body, resources = export_notebook(nb, exporter_cls,
                                                config, template)
    assert exporter.output_mimetype == 'text/html'

    assert body.strip() == '# a title\n\nsome text'
