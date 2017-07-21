import os, logging
from nbconvert.preprocessors import Preprocessor
import traitlets as traits

class LatexCaptions(Preprocessor):
    """ a preprocessor to resolve file paths in the latex_doc metadata section 
    
    retrieve external file paths from metadata,
    resolve where they are, if the path is relative
    make sure that the link points to a single folder
    add 'external_file_paths' and 'bibliopath' (if present) to resources
    
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