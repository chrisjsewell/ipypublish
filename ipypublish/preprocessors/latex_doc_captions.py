import os, logging
from nbconvert.preprocessors import Preprocessor
import traitlets as traits

class LatexCaptions(Preprocessor):
    """ a preprocessor to 
    1. find cells with a latex_doc.caption meta-tag, 
       extract the caption and label to a dict and remove the cell
    2. find cells with the found labels and replace their captions
    
    """
            
    def preprocess(self, nb, resources):
                
        logging.info('extracting caption cells') 
        
        # extract captions
        final_cells = []
        captions = {}
        for cell in nb.cells:
            if hasattr(cell.metadata, 'latex_doc'):
                if hasattr(cell.metadata.latex_doc, 'caption'):
                    captions[cell.metadata.latex_doc.caption] = cell.source.split(r'\n')[0]
                    continue
            final_cells.append(cell)
        nb.cells = final_cells  
        
        # replace captions
        for cell in nb.cells:
            if hasattr(cell.metadata, 'latex_doc'):
                for key in cell.metadata.latex_doc:
                    if hasattr(cell.metadata.latex_doc[key], 'label'):
                        if cell.metadata.latex_doc[key]['label'] in captions:
                            logging.debug('replacing caption for: {}'.format(cell.metadata.latex_doc[key]['label']))
                            cell.metadata.latex_doc[key]['caption'] = captions[cell.metadata.latex_doc[key]['label']]
                
        
        return nb, resources