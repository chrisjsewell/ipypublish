tpl_dict = {
    
'meta_docstring':""" caption and label elements according to latex_doc meta tags  """,
'overwrite':['notebook_output','notebook_all','notebook_input_markdown',
            'notebook_input_code','notebook_input_code_pre','notebook_input_code_post'],
"globals":r"{% set slidenumber = [] %}",


"html_header":r"""

<!--[if IE lte 8]><script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script><![endif]-->

<style>
.figure {
	padding: 0.9em;
	background: #fff;
	margin: 0 auto 1em;
}
.figure img {
	margin: 0 auto;
	display: block;
	max-width: 100%;
}
figure figcaption {
    text-align: left;
}
</style>
""",

'notebook_all':r"""
{%- if cell.metadata.latex_doc: -%}
    {%- if cell.metadata.latex_doc.ignore: -%}
    {%- else -%}
{{ super() }}
    {%- endif %}
{%- else -%}
{{ super() }}
{%- endif %}
""",


'notebook_input_code_pre':r"""
{%- if cell.metadata.latex_doc: -%}
{%- if cell.metadata.latex_doc.code: -%}
{%- if cell.metadata.latex_doc.code.caption: -%}
<br>{{cell.metadata.latex_doc.code.caption}}
{%- endif %}
<div class="input_code">
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
{%- endif %}   
{%- endif %}  
""",
'notebook_input_code':r"""
{%- if cell.metadata.latex_doc: -%}
{%- if cell.metadata.latex_doc.code: -%}
<div class="inner_cell">
<div class="input_area">
{%- if cell.metadata.latex_doc.code.label: -%}
<a id="{{cell.metadata.latex_doc.code.label}}" class="anchor-link" name="#{{cell.metadata.latex_doc.code.label}}"></a>
{% if resources.refslide.setdefault(cell.metadata.latex_doc.code.label, slidenumber | length - 1) %}{% endif %} 
{%- endif %}
{{ cell.source | highlight_code(metadata=cell.metadata) }}
</div>
</div>
{%- endif %}   
{%- endif %}   
""",
'notebook_input_code_post':r"""
{%- if cell.metadata.latex_doc: -%}
{%- if cell.metadata.latex_doc.code: -%}
</div>
</div>
</div>
{%- endif %}   
{%- endif %}   
""",

'notebook_input_markdown':r"""
{{ cell.source  | markdown2html | strip_files_prefix | replace_string("{id_home_prefix}","#") }}
""",

'notebook_output':r"""
{%- if cell.metadata.latex_doc: -%}
    {%- if cell.metadata.latex_doc.figure: -%}
{{ super() }}    
    {%- elif cell.metadata.latex_doc.table: -%}
{{ super() }}    
    {%- elif cell.metadata.latex_doc.equation: -%}
{{ super() }}    
    {%- endif %}   
{%- else -%}
{{ super() }}
{%- endif %}
""",

'notebook_output_latex_pre':r"""
{{ make_figure_pre(cell.metadata) }}
{{ make_table_pre(cell.metadata) }}
{{ make_equation_pre(cell.metadata) }}
""",
'notebook_output_latex_post':r"""
{{ make_figure_post(cell.metadata) }}
{{ make_table_post(cell.metadata) }}
{{ make_equation_post(cell.metadata) }}
""",

'notebook_output_png_pre':r"""
{{ make_figure_pre(cell.metadata) }}
{{ make_table_pre(cell.metadata) }}
{{ make_equation_pre(cell.metadata) }}
""",
'notebook_output_png_post':r"""
{{ make_figure_post(cell.metadata) }}
{{ make_table_post(cell.metadata) }}
{{ make_equation_post(cell.metadata) }}
""",

'notebook_output_jpg_pre':r"""
{{ make_figure_pre(cell.metadata) }}
{{ make_table_pre(cell.metadata) }}
{{ make_equation_pre(cell.metadata) }}
""",
'notebook_output_jpg_post':r"""
{{ make_figure_post(cell.metadata) }}
{{ make_table_post(cell.metadata) }}
{{ make_equation_post(cell.metadata) }}
""",

'notebook_output_svg_pre':r"""
{{ make_figure_pre(cell.metadata) }}
{{ make_table_pre(cell.metadata) }}
{{ make_equation_pre(cell.metadata) }}
""",
'notebook_output_svg_post':r"""
{{ make_figure_post(cell.metadata) }}
{{ make_table_post(cell.metadata) }}
{{ make_equation_post(cell.metadata) }}
""",

'notebook_output_pdf_pre':r"""
{{ make_figure_pre(cell.metadata) }}
{{ make_table_pre(cell.metadata) }}
{{ make_equation_pre(cell.metadata) }}
""",
'notebook_output_pdf_post':r"""
{{ make_figure_post(cell.metadata) }}
{{ make_table_post(cell.metadata) }}
{{ make_equation_post(cell.metadata) }}
""",

'notebook_output_html_pre':r"""
{{ make_figure_pre(cell.metadata) }}
{{ make_table_pre(cell.metadata) }}
{{ make_equation_pre(cell.metadata) }}
""",
'notebook_output_html_post':r"""
{{ make_figure_post(cell.metadata) }}
{{ make_table_post(cell.metadata) }}
{{ make_equation_post(cell.metadata) }}
""",

'jinja_macros':r"""

{% macro make_figure_pre(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.figure: -%}
<figure class='figure'>
    {%- if meta.latex_doc.figure.label: -%}
<a id="{{meta.latex_doc.figure.label}}" class="anchor-link" name="#{{meta.latex_doc.figure.label}}"></a>
    {% if resources.refslide.setdefault(meta.latex_doc.figure.label, slidenumber | length - 1) %}{% endif %} 
    {%- endif %}
    {%- endif %}
{%- endif %}
{%- endmacro %}

{% macro make_figure_post(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.figure: -%}
    
        {%- if meta.latex_doc.figure.caption: -%}
<figcaption>{{meta.latex_doc.figure.caption}}</figcaption>
        {%- endif %}

</figure>
    {%- endif %}
{%- endif %}
{%- endmacro %}

{% macro make_table_pre(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.table: -%}
<figure class='figure'>

        {%- if meta.latex_doc.table.caption: -%}
<figcaption>{{meta.latex_doc.table.caption}}</figcaption>
        {%- endif %}

        {%- if meta.latex_doc.table.label: -%}
<a id="{{meta.latex_doc.table.label}}" class="anchor-link" name="#{{meta.latex_doc.table.label}}"></a>
           {% if resources.refslide.setdefault(meta.latex_doc.table.label, slidenumber | length - 1) %}{% endif %} 
        {%- endif %}
    {%- endif %}

{%- endif %}
{%- endmacro %}

{% macro make_table_post(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.table: -%}
</figure>
    {%- endif %}
{%- endif %}
{%- endmacro %}

{% macro make_equation_pre(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.equation: -%}
    {%- endif %}
{%- endif %}
{%- endmacro %}

{% macro make_equation_post(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.equation: -%}
        {%- if meta.latex_doc.equation.label: -%}
<a id="{{meta.latex_doc.equation.label}}" class="anchor-link" name="#{{meta.latex_doc.equation.label}}"></a>
           {% if resources.refslide.setdefault(meta.latex_doc.equation.label, slidenumber | length - 1) %}{% endif %} 
        {%- endif %}
        {%- if meta.latex_doc.equation.caption: -%}
<div>{{meta.latex_doc.equation.caption}}</div>
        {%- endif %}
    {%- endif %}
{%- endif %}
{%- endmacro %}

""",

}

