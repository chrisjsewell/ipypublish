tpl_dict = {
    
'overwrite':['notebook_all','html_body_start','notebook_input_markdown'],
    
'meta_docstring':'marks up html with slide tags, based on metadata',

"globals":r"""
{% set slidecolumn = [] %}"
{% set sliderow = {} %}"
""",

'html_header':r"""
<style type="text/css">
/* numbering headings */
body { counter-reset: H1; } 	/* Create the counter for H1 */
h1:before {
  content: counter(H1) ". "; 	/* Print the H1 number */
  counter-increment: H1; 	/* Add 1 to next H1 */
}
</style>
""",

'html_body_start':r"""
<div class="reveal">
<div class="slides">
""",
    
'notebook_all':r"""

{%- if cell.metadata.ipyslides == 'skip' -%}
{%- endif -%}

{%- if cell.metadata.ipyslides == 'notes' -%}
<aside class="notes">
{{ super() }}
</aside>
{%- endif -%}

{%- if cell.metadata.ipyslides == 'first_cell' -%}
<section>
{% if slidecolumn.append('1') %}{% endif %}  
{% if sliderow.clear() %}{% endif %}  
{{ super() }}
{%- endif -%}

{%- if cell.metadata.ipyslides == 'horizontalbreak_before' -%}
{{ super() }}
</section>
</section>
{%- endif -%}


{%- if cell.metadata.ipyslides == 'horizontalbreak_after_novertical' -%}
{% if slidecolumn.append('1') %}{% endif %}  
{% if sliderow.clear() %}{% endif %}  
<section>
{{ super() }}
</section>
{%- endif -%}

{%- if cell.metadata.ipyslides == 'horizontalbreak_after_plusvertical' -%}
{% if slidecolumn.append('1') %}{% endif %}  
{% if sliderow.clear() %}{% endif %}  
<section>
<section>
{{ super() }}
</section>
<section>
{%- endif -%}

{%- if cell.metadata.ipyslides == 'horizontalbreak_after' -%}
{% if slidecolumn.append('1') %}{% endif %}  
{% if sliderow.clear() %}{% endif %}  
<section>
<section>
{{ super() }}
{%- endif -%}


{%- if cell.metadata.ipyslides == 'normal' -%}
{{ super() }}
{%- endif -%}

{%- if cell.metadata.ipyslides == 'verticalbreak_after' -%}
{% if sliderow.get('len',[]).append('1') %}{% endif %} 
</section>
<section>
{{ super() }}
{%- endif -%}

{%- if cell.metadata.ipyslides == 'last_cell' -%}
{{ super() }}
</section>
</section>
{%- endif -%}


""",

'notebook_input_markdown':r"""
{{ cell.source  | markdown2html | strip_files_prefix }}
""",


}


