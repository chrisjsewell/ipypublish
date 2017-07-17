#!/usr/bin/env python
"""revel.js slides in the ipypublish format;
- splits titles and sub-titles into separate slides
- removes code cells
- removes latex tags (like \cite{abc})
"""
import re

from ipypublish.html.create_tpl import create_tpl
from ipypublish.html.standard import slides
from ipypublish.html.standard import content
from ipypublish.html.standard import content_tagging
from ipypublish.html.standard import mathjax
from ipypublish.html.standard import widgets
from ipypublish.html.ipypublish import slides_title_pages

oformat = 'Slides'  

def remove_tex_tags(input, **kwargs):
    r"""remove latex tags like \cite{abc} or \todo[color]{stuff} """
    latex_regex = r"\\(?:[^a-zA-Z]|[a-zA-Z]+[*=']?)(?:\[.*?\])?{.*?}"  
    return ''.join(re.split(latex_regex, input))  

_filters = {'remove_tex_tags':remove_tex_tags}
            
config = {'TemplateExporter.filters':_filters,
          'Exporter.filters':_filters}

template = create_tpl([
    content.tpl_dict, content_tagging.tpl_dict,
    mathjax.tpl_dict, widgets.tpl_dict, 
    slides.tpl_dict, slides_title_pages.tpl_dict,
])
