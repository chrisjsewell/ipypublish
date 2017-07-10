""" create the an article in the standard nbconvert format

"""
import os
from latex.create_tplx import create_tplx
from latex.standard import standard_article as doc
from latex.standard import in_out_prompts as prompts
from latex.standard import standard_definitions as defs
from latex.standard import standard_contents as content
from latex.standard import standard_packages as package

create_tplx('created.tplx',
    [package.tplx_dict,defs.tplx_dict,doc.tplx_dict,
    content.tplx_dict,prompts.tplx_dict])

c = get_config() 
c.NbConvertApp.export_format = 'latex'   
c.TemplateExporter.filters = c.Exporter.filters = {}
c.Exporter.template_file = 'created.tplx'