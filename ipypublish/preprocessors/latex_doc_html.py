import os, logging
from nbconvert.preprocessors import Preprocessor
from nbformat.notebooknode import NotebookNode
import traitlets as traits

class LatexDocHTML(Preprocessor):
    r""" processing of ipub metatags, specific to html
    
    - import embedded html files
    - add refmap key to references for {label:reference name} lookup
      e.g. {"fig:test":"fig. 1"}
    - add caption_prefix tag for floats with correct numbering/name
      e.g. cell.metadata.ipub.figure.caption_prefix = "Figure 1: "
    
    """
    
    metapath = traits.Unicode('', help="the path to the meta data").tag(config=True)
    filesfolder = traits.Unicode('', help="the folder to point towards").tag(config=True)
    

    def __init__(self, *args, **kwargs):
        super(LatexDocHTML, self).__init__( *args, **kwargs)

    def resolve_path(self, fpath, filepath):
        """resolve a relative path, w.r.t. another filepath """
        if not os.path.isabs(fpath):
            fpath = os.path.join(os.path.dirname(str(filepath)),fpath)
            fpath = os.path.abspath(fpath)
        return fpath
        
    def create_embed_cell(self, cell):
        """ a new cell, based on embedded html file
        """
        fpath = self.resolve_path(cell.metadata.ipub.embed_html.filepath, self.metapath)
        logging.info('attmepting to embed html in notebook from:'
                            ': {}'.format(fpath))
        if not os.path.exists(fpath):
            logging.warning('file in embed html metadata does not exist'
                            ': {}'.format(fpath))
            return False
        
        with open(fpath) as f:
            embed_data = f.read()
        logging.debug('length of embedding html {}'.format(len(embed_data)))
           
        if '<body>' in embed_data and r'</body>' in embed_data:
            pass#body = embed_data.split('<body>')[1]
            #body = embed_data.split('</body>')[0]
        else:
            logging.warning('file in embed html metadata does not contain a <body> key, using entire file'
                            ': {}'.format(fpath))
            return False

        # if 'head' in embed_data:
        #     if not hasattr(nb.metadata, 'ipub'):
        #         nb.metadata.ipub = {}
        #     if not hasattr(nb.metadata.ipub, 'html_head'):
        #         nb.metadata.ipub.html_head = []
        #     for head in embed_data['head']:
        #         if head not in nb.metadata.ipub.html_head:
        #             nb.metadata.ipub.html_head.append(head)

        cell.outputs.append(NotebookNode({"data": {"text/html": embed_data},
         "execution_count": 0,
         "metadata": {},
         "output_type": "execute_result"}))
        #meta = cell.metadata.ipub.pop('embed_html')
        # newcell = {
        # "cell_type": "code",
        # "execution_count": 0,
        # "metadata": {'ipub':{'figure':meta}},
        # "outputs": [
        # {"data": {"text/html": body},
        #  "execution_count": 0,
        #  "metadata": {},
        #  "output_type": "execute_result"}],
        # "source": [
        # ""]}

        logging.info('successfuly embedded html in cell')
        return cell
        
    def preprocess(self, nb, resources):
        
        logging.info('processing notebook for html output'+
                     ' in ipub metadata to: {}'.format(self.metapath)) 
        
        final_cells = []
        float_count = dict([('figure',0),('table',0),('code',0),('text',0),('error',0)])
        for i, cell in enumerate(nb.cells):
            if hasattr(cell.metadata, 'ipub'):
                if hasattr(cell.metadata.ipub, 'embed_html'):
                    if hasattr(cell.metadata.ipub.embed_html,'filepath'): 
                        self.create_embed_cell(cell)
                    else:
                        logging.warning('cell {} has no filepath key in its metadata.embed_html'.format(i)) 
                        
                for floattype, floatabbr in [('figure','fig.'),('table','tbl.'),('code','code'),
                                              ('text','text'),('error','error')]:
                    if floattype in cell.metadata.ipub:
                        float_count[floattype] += 1
                        if not isinstance(cell.metadata.ipub[floattype],dict):
                            continue
                        cell.metadata.ipub[floattype]['caption_prefix'] = '<b>{0} {1}:</b> '.format(floattype.capitalize(),float_count[floattype])
                        if 'label' in cell.metadata.ipub[floattype]:
                            resources.setdefault('refmap',{})[cell.metadata.ipub[floattype]['label']] = '{0} {1}'.format(floatabbr,float_count[floattype])
                    
            final_cells.append(cell)
        nb.cells = final_cells                    
        
        return nb, resources