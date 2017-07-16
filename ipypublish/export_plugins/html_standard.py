#!/usr/bin/env python
"""
standard nbconvert html output
"""

from ipypublish.html.create_tpl import create_tpl
from ipypublish.html.standard import document
from ipypublish.html.standard import content
from ipypublish.html.standard import mathjax
from ipypublish.html.standard import widgets
from ipypublish.html.standard import inout_prompt

oformat = 'HTML'   
config = {}
template = create_tpl([
    document.tpl_dict, content.tpl_dict, 
    mathjax.tpl_dict, widgets.tpl_dict, 
    inout_prompt.tpl_dict
])