r"""html in standard nbconvert format, but with 
- a table of contents 
- toggle buttons for showing/hiding code & output cells
- converts or removes (if no converter) latex tags (like \cite{abc}, \ref{})

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
from ipypublish.preprocessors.latex_doc import LatexDocLinks
from ipypublish.preprocessors.latex_doc_html import LatexDocHTML
from ipypublish.preprocessors.latextags_to_html import LatexTagsToHTML
from ipypublish.filters.replace_string import replace_string

oformat = 'HTML'   
config = {'TemplateExporter.filters':{'replace_string':replace_string},
          'Exporter.filters':{'replace_string':replace_string},
          'Exporter.preprocessors':[LatexDocLinks,LatexDocHTML,LatexTagsToHTML]}

template = create_tpl([
    document.tpl_dict, 
    content.tpl_dict, content_tagging.tpl_dict, 
    mathjax.tpl_dict, widgets.tpl_dict, 
#    inout_prompt.tpl_dict, 
    toggle_buttons.tpl_dict, toc_sidebar.tpl_dict, 
    latex_doc.tpl_dict
])

