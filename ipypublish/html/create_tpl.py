#!/usr/bin/env python

"""
create template

philosophy is only turn stuff on when we want

http://nbconvert.readthedocs.io/en/latest/customizing.html#Template-structure
http://nbconvert.readthedocs.io/en/latest/api/exporters.html#nbconvert.exporters.TemplateExporter

"""

TPL_OUTLINE = r"""
<!-- A html document --> 
<!-- {meta_docstring} --> 


{{%- extends 'display_priority.tpl' -%}}

%% HTML Setup
%% ====================

{{%- block header %}}
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
{{%- block html_head -%}}
    {html_header}
{{%- endblock html_head -%}}
</head>
{{%- endblock header -%}}

{{% block body %}}
 <body>
 {html_body_start}
 {{{{ super() }}}}
 {html_body_end}
 </body>   
{{%- endblock body %}}

{{%- block footer %}}
    {html_footer}
</html>
{{%- endblock footer-%}}

%% Notebook Input
%% ==============

{{%- block any_cell scoped %}}
{notebook_all}
{{% endblock any_cell %}}

{{% block input_group -%}}
<div class="input_code">
<div class="cell border-box-sizing code_cell rendered">
<div class="input">
{notebook_input}
</div>
</div>
</div>
{{% endblock input_group %}}

{{% block in_prompt -%}}
{notebook_input_prompt}
{{%- endblock in_prompt %}}

{{% block input scoped %}}
<div class="inner_cell">
<div class="input_area">
{notebook_input_code}
</div>
</div>
{{% endblock input %}}

{{% block rawcell scoped %}}
<div class="input_raw">
<div class="cell border-box-sizing text_cell rendered">
<div class="inner_cell">
<div class="text_cell_render border-box-sizing rendered_html">
{notebook_input_raw}
</div>
</div>
</div>
</div>
{{% endblock rawcell %}}

{{% block markdowncell scoped %}}
<div class="input_markdown">
<div class="cell border-box-sizing text_cell rendered">
<div class="inner_cell">
<div class="text_cell_render border-box-sizing rendered_html">
{notebook_input_markdown}
</div>
</div>
</div>
</div>
{{% endblock markdowncell %}}

{{% block unknowncell scoped %}}
<div class="input_unknown">
{notebook_input_unknown}
</div>
{{% endblock unknowncell %}}

%% Notebook Outbook
%% ================

{{% block output %}}
<div class="output_area">
{notebook_output_prompt}
{{{{ super() }}}}
</div>
{{% endblock output %}}

% Redirect execute_result to display data priority.
{{%- block execute_result scoped %}}
    {{%- set extra_class="output_execute_result" -%}}
    {{% block data_priority scoped %}}
{notebook_output}
    {{% endblock %}}
    {{%- set extra_class="" -%}}
{{% endblock execute_result %}}

{{% block error %}}
<div class="output_subarea output_text output_error">
<pre>
{notebook_output_error}
</pre>
</div>
{{% endblock error %}}

{{% block traceback_line %}}
 <div class="output_traceback">
{notebook_output_traceback}
</div>
{{% endblock traceback_line %}}

{{% block data_text %}}
<div class="output_text output_subarea {{{{ extra_class }}}}">
<pre>
{notebook_output_text}
</pre>
</div>
{{% endblock data_text %}}

{{% block data_latex -%}}
<div class="output_latex output_subarea {{{{ extra_class }}}}">
{notebook_output_latex}
</div>
{{% endblock data_latex %}}


{{% block stream_stdout %}}
<div class="output_subarea output_stream output_stdout output_text">
<pre>
{notebook_output_stream_stdout}
</pre>
</div>
{{% endblock stream_stdout %}}
{{% block stream_stderr %}}
 <div class="output_subarea output_stream output_stderr output_text">
 <pre>
{notebook_output_stream_stderr}
</pre>
</div>
{{% endblock stream_stderr %}}

{{%- block data_markdown -%}}
<div class="output_markdown rendered_html output_subarea {{{{ extra_class }}}}">
{notebook_output_markdown}
</div>
{{% endblock data_markdown %}}

{{%- block data_jpg -%}}
<div class="output_image output_jpeg output_subarea {{{{ extra_class }}}}">
	{notebook_output_jpg}
</div>
{{%- endblock data_jpg -%}}

{{%- block data_png -%}}
<div class="output_image output_png output_subarea {{{{ extra_class }}}}">
	{notebook_output_png}
</div>
{{%- endblock data_png -%}}

{{%- block data_svg -%}}
<div class="output_image output_svg output_subarea {{{{ extra_class }}}}">
	{notebook_output_svg}
</div>
{{%- endblock data_svg -%}}

{{%- block data_pdf -%}}
<div class="output_pdf output_subarea {{{{ extra_class }}}}">
	{notebook_output_pdf}
</div>
{{%- endblock -%}}

{{% block data_html -%}}
<div class="output_html rendered_html output_subarea {{{{ extra_class }}}}">
{notebook_output_html}
</div>
{{% endblock data_html%}}

{{%- block data_javascript scoped %}}
{{% set div_id = uuid4() %}}
<div id="{{ div_id }}"></div>
<div class="output_subarea output_javascript {{{{ extra_class }}}}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
{notebook_output_javascript}
</script>
</div>
{{%- endblock -%}}

{{%- block data_widget_state scoped %}}
{{% set div_id = uuid4() %}}
{{% set datatype_list = output.data | filter_data_type %}} 
{{% set datatype = datatype_list[0]%}} 
<div id="{{ div_id }}"></div>
<div class="output_subarea output_widget_state {{{{ extra_class }}}}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
</script>
<script type="{{ datatype }}">
	{notebook_output_widget_state}
</script>
</div>
{{%- endblock data_widget_state -%}}

{{%- block data_widget_view scoped %}}
{{% set div_id = uuid4() %}}
{{% set datatype_list = output.data | filter_data_type %}} 
{{% set datatype = datatype_list[0]%}} 
<div id="{{ div_id }}"></div>
<div class="output_subarea output_widget_view {{{{ extra_class }}}}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
</script>
<script type="{{ datatype }}">
	{notebook_output_widget_view}
</script>
</div>
{{%- endblock data_widget_view -%}}

%% Jinja Macros
%% ================

{jinja_macros}
"""

def create_tpl(tpl_dicts=(),outpath=None):
    """ build an html jinja template from multiple dictionaries,
    specifying fragments of the template to insert a specific points
                
    if a tpl_dict contains the key "overwrite", 
    then its value should be a list of keys,
    such that these key values overwrite any entries before
                
    Parameters
    ----------
    tpl_dicts: list of dicts
    outpath: str
        if not None, output template to file
    outline : dict
        the outline jinja template
    
    """
    outline=TPL_OUTLINE
    tpl_sections={
    'meta_docstring':'',

    'html_header':'',
    'html_body_start':'',
    'html_body_end':'',
    'html_footer':'',
    
    'notebook_all':'',

    'notebook_input':'',
    'notebook_input_prompt':'',
    'notebook_input_code':'',
    'notebook_input_raw':'',
    'notebook_input_markdown':'',
    'notebook_input_unknown':'',

    'notebook_output':'',
    'notebook_output_prompt':'',
    'notebook_output_text':'',
    'notebook_output_error':'',
    'notebook_output_traceback':'',
    'notebook_output_stream_stderr':'',
    'notebook_output_stream_stdout':'',
    'notebook_output_latex':'',
    'notebook_output_markdown':'',
    'notebook_output_png':'',
    'notebook_output_jpg':'',
    'notebook_output_svg':'',
    'notebook_output_pdf':'',
    'notebook_output_html':'',
    'notebook_output_javascript':'',
    'notebook_output_widget_state':'',
    'notebook_output_widget_view':'',

    'jinja_macros':''}
    
    for i, tpl_dict in enumerate(tpl_dicts):
        if 'overwrite' in tpl_dict:
            overwrite = tpl_dict.pop('overwrite')
        else:
            overwrite = []
        for key,val in tpl_dict.items():
            if key not in tpl_sections:
                raise ValueError(
                '{0} from tpl_dict {1} not in outline tpl section'.format(key,i+1))
            if key in overwrite:
                tpl_sections[key] = val
            else:
                tpl_sections[key] = tpl_sections[key]+'\n'+val

    outline =  outline.format(**tpl_sections) 
    
    if outpath is not None: 
        with open(outpath,'w') as f:
            f.write(outline)
        return
    return outline
