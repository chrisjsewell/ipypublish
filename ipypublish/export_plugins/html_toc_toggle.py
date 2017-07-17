"""html in standard nbconvert format, 
but with a table of contents 
and toggle buttons for showing/hiding code & output cells
"""

from ipypublish.html.create_tpl import create_tpl
from ipypublish.html.standard import document
from ipypublish.html.standard import content
from ipypublish.html.standard import content_tagging
from ipypublish.html.standard import mathjax
from ipypublish.html.standard import widgets
from ipypublish.html.standard import inout_prompt
from ipypublish.html.ipypublish import toc_sidebar
from ipypublish.html.ipypublish import toggle_buttons

oformat = 'HTML'   
config = {'TemplateExporter.filters':{},
          'Exporter.filters':{}}

template = create_tpl([
    document.tpl_dict, 
    content.tpl_dict, content_tagging.tpl_dict, 
    mathjax.tpl_dict, widgets.tpl_dict, 
    inout_prompt.tpl_dict, 
    toggle_buttons.tpl_dict, toc_sidebar.tpl_dict, 
])

