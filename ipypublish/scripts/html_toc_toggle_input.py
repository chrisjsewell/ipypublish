""" create html with a table of contents 
and toggleable input code cells

"""

oformat = 'HTML'   
config = {'TemplateExporter.filters':{},
          'Exporter.filters':{}}

template="""
{%- extends 'full.tpl' -%}

{%- block header -%}
{{ super() }}

<script>
code_show=true; 
function code_toggle() {
 if (code_show){
 $('div.input').hide();
 } else {
 $('div.input').show();
 }
 code_show = !code_show
} 
$( document ).ready(code_toggle);
</script>

<form action="javascript:code_toggle()">
	<input type="submit" value="Toggle Input Code">
</form>

<style>
.sidebar-wrapper { /* Move down to accomodate button */
	margin-top: 35px;
}
form {
  /* Just to center the form on the page */
  margin: 0 auto;
  height: 25px;
  width: 150px;
  align:center;
  text-align:center;
  position: fixed;

  /* To see the limits of the form */
  padding: 1px;
  border: 1px solid #CCC;
  border-radius: 1px;
}
</style>

<link rel="stylesheet" href="https://code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">

<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.9.1/jquery-ui.min.js"></script>

<style>  /* defined here in case the main.css below cannot be loaded */
.lev1 {margin-left: 80px}
.lev2 {margin-left: 100px}
.lev3 {margin-left: 120px}
.lev4 {margin-left: 140px}
.lev5 {margin-left: 160px}
.lev6 {margin-left: 180px}
</style>

<link rel="stylesheet" type="text/css" href="https://rawgit.com/ipython-contrib/jupyter_contrib_nbextensions/master/src/jupyter_contrib_nbextensions/nbextensions/toc2/main.css">

<script src="https://rawgit.com/ipython-contrib/jupyter_contrib_nbextensions/master/src/jupyter_contrib_nbextensions/nbextensions/toc2/toc2.js"></script>

<script>
$( document ).ready(function(){
            var cfg={'threshold':{{ nb.get('metadata', {}).get('toc', {}).get('threshold', '3') }},     // depth of toc (number of levels)
             'number_sections': {{ 'true' if nb.get('metadata', {}).get('toc', {}).get('number_sections', False) else 'false' }},  // sections numbering
             'toc_cell': false,          // useless here
             'toc_window_display': true, // display the toc window
             "toc_section_display": "block", // display toc contents in the window
             'sideBar':{{ 'true' if nb.get('metadata', {}).get('toc', {}).get('sideBar', False) else 'false' }},             // sidebar or floating window
             'navigate_menu':false       // navigation menu (only in liveNotebook -- do not change)
            }
            var st={};                  // some variables used in the script
            st.rendering_toc_cell = false;
            st.config_loaded = false;
            st.extension_initialized=false;
            st.nbcontainer_marginleft = $('#notebook-container').css('margin-left')
            st.nbcontainer_marginright = $('#notebook-container').css('margin-right')
            st.nbcontainer_width = $('#notebook-container').css('width')
            st.oldTocHeight = undefined
            st.cell_toc = undefined;
            st.toc_index=0;
            // fire the main function with these parameters
            table_of_contents(cfg,st);
    });
</script>

{%- endblock header -%}
"""