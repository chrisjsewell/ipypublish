import os, logging, json
from nbconvert.preprocessors import Preprocessor
import traitlets as traits

class LatexDocHTML(Preprocessor):
    """ processing of latex_doc metatags, specific to html
    
    add prefixes to figure/table/code captions, with correct numbering
    add reference naming lookup to resources
    import embedded html files
    
    NB: if there are captions in markdown cells, 
    then should be applied after LatexDocLinks, in order to have captions with correct numbering
    
    """
    
    metapath = traits.Unicode('', help="the path to the meta data").tag(config=True)
    filesfolder = traits.Unicode('', help="the folder to point towards").tag(config=True)
    

    def __init__(self, *args, **kwargs):
        #self.fignums = {'figure':{},'table':{},'code'} 
        super(LatexDocHTML, self).__init__( *args, **kwargs)

    def resolve_path(self, fpath, filepath):
        """resolve a relative path, w.r.t. another filepath """
        if not os.path.isabs(fpath):
            fpath = os.path.join(os.path.dirname(str(filepath)),fpath)
            fpath = os.path.abspath(fpath)
        return fpath
        
    def create_embed_cell(self, meta):
        """ a new cell, based on embedded html file
        """
        fpath = self.resolve_path(meta.latex_doc.embed_file, self.metapath)
        if not os.path.exists(fpath):
            logging.warning('file in embed metadata does not exist'
                            ': {}'.format(fpath))
            return False
        try:
            embed_data = json.load(fpath)
        except:
            logging.warning('file in embed metadata is not formatted correctly'
                            ': {}'.format(fpath))    
            return False        
        if 'body' not in embed_data:
            logging.warning('file in embed metadata does not contain a body key'
                            ': {}'.format(fpath))    
            return False                    

        if 'head' in embed_data:
            if not hasattr(nb.metadata, 'latex_doc'):
                nb.metadata.latex_doc = {}
            if not hasattr(nb.metadata.latex_doc, 'html_head'):
                nb.metadata.latex_doc.html_head = []
            for head in embed_data['head']:
                if head not in nb.metadata.latex_doc.html_head:
                    nb.metadata.latex_doc.html_head.append(head)

        newcell = {
        "cell_type": "code",
        "execution_count": 0,
        "metadata": {'latex_doc':{'html':meta}},
        "outputs": [
        {"data": {"text/html": embed_data['body']},
         "execution_count": 0,
         "metadata": {},
         "output_type": "execute_result"}],
        "source": [
        ""]}
        return newcell
        
    def preprocess(self, nb, resources):
        
        logging.info('processing notebook for html output'+
                     ' in latex_doc metadata to: {}'.format(self.metapath)) 
        
        final_cells = []
        float_count = dict([('figure',0),('table',0),('code',0)])
        for cell in nb.cells:
            if hasattr(cell.metadata, 'latex_doc'):
                if hasattr(cell.metadata.latex_doc, 'embed_file'):
                    newcell = self.create_embed_cell(nb, cell.metadata)
                    if newcell:
                        final_cells.append(newcell)
                        
                for floattype, floatabbr in [('figure','fig.'),('table','tbl.'),('code','code')]:
                    if floattype in cell.metadata.latex_doc:
                        float_count[floattype] += 1
                        if 'caption' in cell.metadata.latex_doc[floattype]:
                            newcaption =  '<b>{0} {1}: </b>'.format(floattype.capitalize(),float_count[floattype]) + cell.metadata.latex_doc[floattype].caption
                            cell.metadata.latex_doc[floattype].caption = newcaption
                        if 'label' in cell.metadata.latex_doc[floattype]:
                            resources.setdefault('refmap',{})[cell.metadata.latex_doc[floattype]['label']] = '{0} {1}'.format(floatabbr,float_count[floattype])
                    
            final_cells.append(cell)
        nb.cells = final_cells                    
        
        return nb, resources