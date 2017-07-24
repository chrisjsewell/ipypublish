import os, logging
from nbconvert.preprocessors import Preprocessor
import traitlets as traits

class LatexCaptions(Preprocessor):
    """ a preprocessor to 
    1. find cells with a latex_doc.caption meta-tag, 
       extract the caption and label to a dict and remove the cell
    2. find cells with the found labels and replace their captions
    
    """
    
    add_prefix = traits.Bool(False,help="add float type/number prefix to caption (from caption_prefix tag)").tag(config=True)
            
    def preprocess(self, nb, resources):
                
        logging.info('extracting caption cells') 
        
        # extract captions
        final_cells = []
        captions = {}
        for cell in nb.cells:
            if hasattr(cell.metadata, 'latex_doc'):
                if hasattr(cell.metadata.latex_doc, 'caption'):
                                        
                    if cell.cell_type == 'markdown':
                        capt = cell.source.split(r'\n')[0]
                        captions[cell.metadata.latex_doc.caption] = capt
                        continue
                    #TODO can outputs have more than one item in its list?
                    elif cell.cell_type == 'code':
                        if "text/latex" in cell.outputs[0].get('data',{}):
                            capt = cell.outputs[0].data["text/latex"].split(r'\n')[0]
                            captions[cell.metadata.latex_doc.caption] = capt
                            continue
                        elif "text/plain" in cell.outputs[0].get('data',{}):
                            capt = cell.outputs[0].data["text/plain"].split(r'\n')[0]
                            captions[cell.metadata.latex_doc.caption] = capt
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
                            
                    # add float type/number prefix to caption, if required
                    if self.add_prefix:
                        if hasattr(cell.metadata.latex_doc[key], 'caption'):
                            if hasattr(cell.metadata.latex_doc[key], 'caption_prefix'):                    
                                newcaption = cell.metadata.latex_doc[key].caption_prefix + cell.metadata.latex_doc[key].caption
                                cell.metadata.latex_doc[key].caption = newcaption
                    
        
        return nb, resources