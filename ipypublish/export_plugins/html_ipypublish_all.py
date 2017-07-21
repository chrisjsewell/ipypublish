r"""html in ipypublish format, preprocessed with default metadata tags 
- a table of contents 
- toggle buttons for showing/hiding code & output cells
- converts or removes (if no converter) latex tags (like \cite{abc}, \ref{})
- all code/errors/output is shown unless tagged otherwise
"""

from ipypublish.html.create_tpl import create_tpl
from ipypublish.html.standard import document
from ipypublish.html.standard import content
from ipypublish.html.standard import content_tagging
from ipypublish.html.standard import mathjax
from ipypublish.html.standard import widgets
#from ipypublish.html.standard import inout_prompt
from ipypublish.html.ipypublish import toc_sidebar
from ipypublish.html.ipypublish import toggle_buttons
from ipypublish.html.ipypublish import latex_doc
from ipypublish.preprocessors.latex_doc_links import LatexDocLinks
from ipypublish.preprocessors.latex_doc_captions import LatexCaptions
from ipypublish.preprocessors.latex_doc_html import LatexDocHTML
from ipypublish.preprocessors.latextags_to_html import LatexTagsToHTML
from ipypublish.filters.replace_string import replace_string
from ipypublish.preprocessors.latex_doc_defaults import MetaDefaults

cell_defaults = {
  "latex_doc": {
    "figure": {
      "placement": "H"
    },
    "table": {
      "placement": "H"
    },
    "equation": True,
    "text": True,
    "code":True,
    "error":True
  }
}

nb_defaults={
"latex_doc": {
  "titlepage":{},
  "toc": True,
  "listfigures": True,
  "listtables": True,
  "listcode": True,
  }
}

oformat = 'HTML'   
config = {'TemplateExporter.filters':{'replace_string':replace_string},
          'Exporter.filters':{'replace_string':replace_string},
          'Exporter.preprocessors':[MetaDefaults,LatexDocLinks,LatexDocHTML,LatexTagsToHTML,LatexCaptions],
          'MetaDefaults.cell_defaults':cell_defaults,
          'MetaDefaults.nb_defaults':nb_defaults}
          
template = create_tpl([
    document.tpl_dict, 
    content.tpl_dict, content_tagging.tpl_dict, 
    mathjax.tpl_dict, widgets.tpl_dict, 
#    inout_prompt.tpl_dict, 
    toggle_buttons.tpl_dict, toc_sidebar.tpl_dict, 
    latex_doc.tpl_dict
])

