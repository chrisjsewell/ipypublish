#!/usr/bin/env python
"""
standard nbconvert html output
"""

from ipypublish.html.create_tpl import create_tpl
from ipypublish.html.standard import slides
from ipypublish.html.standard import content
from ipypublish.html.standard import mathjax
from ipypublish.html.standard import widgets

oformat = 'Slides'   
config = {}
template = create_tpl([
    content.tpl_dict, 
    mathjax.tpl_dict, widgets.tpl_dict, 
    slides.tpl_dict
])
