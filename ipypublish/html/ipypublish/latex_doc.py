tpl_dict = {
    
'meta_docstring':""" caption and label elements according to latex_doc meta tags  """,
# using: https://tympanus.net/codrops/2013/05/02/automatic-figure-numbering-with-css-counters/
# .figure figcaption {
#     font-weight: 700;
#     text-transform: uppercase;
#     letter-spacing: 2px;
#     font-size: 0.8em;
#     padding: .5em;
#     text-align: center;
#     color: #fff;
#     background: #f5bca8;
# }

# .article {
#     counter-reset: figures;}
# .figure-figure .figure figcaption {
#     counter-increment: figures;}
# .figure-figure .figure figcaption:before {
#     content: 'Figure ' counter(figures) ': ';}

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
    {%- endif %}
{%- endif %}
{%- endmacro %}

{% macro make_figure_post(meta) -%}
{%- if meta.latex_doc: -%}
    {%- if meta.latex_doc.figure: -%}
        {%- if meta.latex_doc.figure.label: -%}
<a id="{{meta.latex_doc.figure.label}}" class="anchor-link" name="#{{meta.latex_doc.figure.label}}"></a>
        {%- endif %}
        {%- if meta.latex_doc.figure.caption: -%}
<figcaption><b>Figure</b>: {{meta.latex_doc.figure.caption}}</figcaption>
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
<figcaption><b>Table</b>: {{meta.latex_doc.table.caption}}</figcaption>
        {%- endif %}
        {%- if meta.latex_doc.table.label: -%}
<a id="{{meta.latex_doc.table.label}}" class="anchor-link" name="#{{meta.latex_doc.table.label}}"></a>
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
        {%- endif %}
        {%- if meta.latex_doc.equation.caption: -%}
<div><b>Equation</b>: {{meta.latex_doc.equation.caption}}</div>
        {%- endif %}
    {%- endif %}
{%- endif %}
{%- endmacro %}

""",

}

