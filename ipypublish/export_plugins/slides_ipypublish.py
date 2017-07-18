#!/usr/bin/env python
r"""revel.js slides in the ipypublish format;
- splits titles and sub-titles into separate slides
- removes code cells
- converts or removes (if no converter) latex tags (like \cite{abc}, \ref{})
"""
import re
import logging

from ipypublish.html.create_tpl import create_tpl
from ipypublish.html.standard import slides
from ipypublish.html.standard import content
from ipypublish.html.standard import content_tagging
from ipypublish.html.standard import mathjax
from ipypublish.html.standard import widgets
from ipypublish.html.ipypublish import latex_doc
from ipypublish.html.ipypublish import slides_mkdown
from ipypublish.preprocessors.latex_doc import LatexDocLinks
from ipypublish.preprocessors.latextags_to_html import LatexTagsToHTML

oformat = 'Slides'  

_filters = {}
            
config = {'TemplateExporter.filters':_filters,
          'Exporter.filters':_filters,
          'Exporter.preprocessors':[LatexDocLinks,LatexTagsToHTML]}

template = create_tpl([
    content.tpl_dict, content_tagging.tpl_dict,
    mathjax.tpl_dict, widgets.tpl_dict, 
    slides.tpl_dict, slides_mkdown.tpl_dict,
    latex_doc.tpl_dict
])
