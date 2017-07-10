""" create the an article in the ipypublish format;
only output with metadata tags
but also with framed input code

"""

from latex.create_tplx import create_tplx
from latex.standard import standard_definitions as defs
from latex.standard import standard_packages as package
from latex.ipypublish import doc_article as doc
from latex.ipypublish import biblio_natbib as bib
from latex.ipypublish import contents_output as output
from latex.ipypublish import contents_framed_code as code
from latex.ipypublish import front_pages as title
from latex.ipypublish.filters import remove_dollars, first_para, create_key

create_tplx('created.tplx',
    [p.tplx_dict for p in [package,defs,doc,title,bib,output,code]])


c = get_config() 
c.NbConvertApp.export_format = 'latex'   
c.TemplateExporter.filters = c.Exporter.filters = {'remove_dollars': remove_dollars,
                                                    'first_para': first_para,
                                                    'create_key': create_key}
c.Exporter.template_file = 'created.tplx'