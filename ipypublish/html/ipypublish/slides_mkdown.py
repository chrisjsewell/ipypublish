tpl_dict = {
    
'meta_docstring':"""sets markdown main titles (with one #) as their own slides, 
remove code cells """,

"overwrite":['notebook_all', 
'notebook_input_code','notebook_input_code_pre','notebook_input_code_post'],

# don't use slide meta tags at present
'notebook_all':'{{ super() }}',
# new slide on header, and sub-header
'notebook_input_markdown_pre':r"""
{%- if cell.source[0] == '#' -%}
    {%- if cell.source[1] == '#' -%}
        {%- if cell.source[2] == '#' -%}

        {%- else -%}
</section>
<section>
        {%- endif -%}
    {%- else -%}
</section>
<section>
    {%- endif -%}
{%- endif -%}
""",

# remove all code
'notebook_input_code_pre':r"""
""",
'notebook_input_code_post':r"""
""",
'notebook_input_code':r"""
""",


}

