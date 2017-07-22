import logging,copy,re
from nbconvert.preprocessors import Preprocessor
from nbformat.notebooknode import NotebookNode
import traitlets as traits

class FinalCells(object):
    """ a class that stores cells
    """
    def __init__(self,header_slide):
        self.cells = []
        if header_slide:
            self.horizontalbreak_after = 'horizontalbreak_after_plusvertical'
        else:
            self.horizontalbreak_after = 'horizontalbreak_after'
        
    def mkdcell(self, source,metadata,slidetype):
        meta = copy.deepcopy(metadata)
        meta.ipyslides = slidetype    
        self.append(NotebookNode({"cell_type": "markdown",
                "source": '\n'.join(source),
                "metadata":meta}))
                
    def append(self,cell):
        last = self.last()
        if not last:
            pass
        elif cell.metadata.ipyslides == 'verticalbreak_after':
            pass#last.metadata.ipyslides = 'verticalbreak_above'
        elif cell.metadata.ipyslides == self.horizontalbreak_after:
            #if last.metadata.ipyslides == 'before_header':
            #    last.metadata.ipyslides == 'between_headers'
            if not last.metadata.ipyslides == self.horizontalbreak_after:
                last.metadata.ipyslides = 'horizontalbreak_before'
            else:
                last.metadata.ipyslides = 'horizontalbreak_after_novertical'                
        self.cells.append(cell)
        
    def first(self):
        for cell in self.cells:
            if not cell.metadata.ipyslides in ['skip','notes']:
                return cell
        return False
    def last(self):
        for cell in reversed(self.cells):
            if not cell.metadata.ipyslides in ['skip','notes']:
                return cell
        return False
    def finalize(self):
        if not self.first():
            return False
        if self.first().metadata.ipyslides == 'normal':
            self.first().metadata.ipyslides = 'first_cell'
        if self.last().metadata.ipyslides == 'normal':
            self.last().metadata.ipyslides = 'last_cell'
        return True
   
def is_header(line,max_level):
    """if max_level is 0 assumes all headers ok"""
    if max_level:
        return len(re.findall('^#{{1,{0}}} .+'.format(max_level),line))>0
    else:
        return len(re.findall('^#* .+',line))>0        
    
class MarkdownSlides(Preprocessor):
    """ a preprocessor to setup the notebook as an ipyslideshow,
    according to a set of rules 
    
    - respect existing 'slideshow.notes' and 'slideshow.skip' cell tags
    - markdown cells containaing # headers are broken into individual cells
    - if latex_doc=True, 
        - any cells where latex_doc.ignore=True is set to 'skip'
        - any code cells with no other latex_doc tags are set to 'skip'
    - any header level >= column_level starts a new column
    - else, any header level >= row_level starts a new row
    - if max_cells is not 0, then breaks to a new row after <max_cells> cells
    
    """
    
    column_level = traits.Integer(1,min=0, help='maximum header level for new columns (0 indicates no maximum)').tag(config=True)
    row_level = traits.Integer(0,min=0, help='maximum header level for new rows (0 indicates no maximum)').tag(config=True)
    header_slide = traits.Bool(False,help='if True, make the first header in a column appear on its own slide').tag(config=True)
    max_cells = traits.Integer(0,min=0,help='maximum number of nb cells per slide (0 indicates no maximum)').tag(config=True)

    latex_doc = traits.Bool(True,help='if True, obey latex_doc tags')
            
    def preprocess(self, nb, resources):
                
        logging.info('creating slides based on markdown and existing slide tags') 
        latexdoc_tags = ['code','error','table','equation','figure','text']
        # break up titles
        cells_in_slide = 0
        final_cells = FinalCells(self.header_slide)
        for i, cell in enumerate(nb.cells):
            
            # Make sure every cell has a slideshow meta tag
            cell.metadata.slideshow = cell.metadata.get('slideshow', NotebookNode())
            cell.metadata.slideshow.slide_type = cell.metadata.slideshow.get('slide_type', '-')
            cell.metadata.ipyslides = cell.metadata.get('ipyslides', NotebookNode()) 
            if self.latex_doc:               
                cell.metadata.latex_doc = cell.metadata.get('latex_doc', NotebookNode())                
            
            # ignore these cells 
            if cell.metadata.slideshow.slide_type == 'skip':
                cell.metadata.ipyslides = 'skip'
                final_cells.append(cell)
                continue
            # ignore these cells 
            if cell.metadata.slideshow.slide_type == 'notes':
                cell.metadata.ipyslides = 'notes'
                final_cells.append(cell)
                continue

            if not cell.cell_type == "markdown":
                if cell.metadata.latex_doc and self.latex_doc:
                    if cell.metadata.latex_doc.get('ignore',False):
                        if cell.metadata.latex_doc.ignore:
                            cell.metadata.ipyslides = 'skip'
                            final_cells.append(cell)
                            continue      
                    #TODO this doesn't test if the data is actually available to be output                  
                    if not any([cell.metadata.latex_doc.get(typ,False) for typ in latexdoc_tags]):
                        cell.metadata.ipyslides = 'skip'
                        final_cells.append(cell)
                        continue                                                
                        
                if cells_in_slide > self.max_cells and self.max_cells:
                    cell.metadata.ipyslides  = 'verticalbreak_after'
                    cells_in_slide = 1
                else:
                    cell.metadata.ipyslides  = 'normal'
                    cells_in_slide += 1
                final_cells.append(cell)
                continue

            nonheader_lines = []
            for line in cell.source.split('\n'):
                
                if is_header(line,self.column_level):
                    if nonheader_lines:
                        if cells_in_slide > self.max_cells and self.max_cells:
                            final_cells.mkdcell(nonheader_lines,cell.metadata,'verticalbreak_after')                           
                            cells_in_slide = 1
                        else:
                            cells_in_slide += 1
                            final_cells.mkdcell(nonheader_lines,cell.metadata,'normal')
                        current_lines = []                                                
    
                    if self.header_slide:
                        final_cells.mkdcell([line],cell.metadata,'horizontalbreak_after_plusvertical')
                    else:
                        final_cells.mkdcell([line],cell.metadata,'horizontalbreak_after')
                    cells_in_slide = 1

                elif is_header(line,self.row_level):
                    if nonheader_lines:
                        if cells_in_slide > self.max_cells and self.max_cells:
                            final_cells.mkdcell(nonheader_lines,cell.metadata,'verticalbreak_after')                           
                            cells_in_slide = 1
                        else:
                            cells_in_slide += 1
                            final_cells.mkdcell(nonheader_lines,cell.metadata,'normal')
                        current_lines = []                                                
    
                    final_cells.mkdcell([line],cell.metadata,'verticalbreak_after')
                    cells_in_slide = 1
                else:
                    nonheader_lines.append(line)

            if nonheader_lines:
                if cells_in_slide > self.max_cells and self.max_cells:
                    final_cells.mkdcell(nonheader_lines,cell.metadata,'verticalbreak_after')
                    cells_in_slide = 1
                else:
                    cells_in_slide += 1
                    final_cells.mkdcell(nonheader_lines,cell.metadata,'normal')

        if not final_cells.finalize():
            logging.warning('no cells available for slideshow')
        nb.cells = final_cells.cells                  
        
        return nb, resources