import os, logging, re
from nbconvert.preprocessors import Preprocessor
import traitlets as traits
import bibtexparser

import string
# python 3 to 2 compatibility
try:
    basestring
except NameError:
    basestring = str

class DefaultFormatter(string.Formatter):
    def __init__(self, default=''):
        self.default=default

    def get_value(self, key, args, kwds):
        if isinstance(key, basestring):
            return kwds.get(key, self.default.format(key))
        else:
            Formatter.get_value(key, args, kwds)
            
class LatexTagsToHTML(Preprocessor):
    r""" a preprocessor to find latex tags (like \cite{abc} or \todo[color]{stuff}) and:
    1. attempt to process them into a html friendly format
    2. remove them entirely if this is not possible
    
    for \ref or \cref,  attempts to use resources.refmap to map labels to reference names
    for labels not found in resources.refmap
    the reference name is '<name> <number>', where;
    - <name> is either ref of, if labelbycolon is True and the label has a colon, all text before the colon
    - <number> iterate by order of first appearance of a particular label
    
    NB: should be applied after LatexDocHTML, if you want resources.refmap to be available
    
    """
    
    regex = traits.Unicode(r"\\(?:[^a-zA-Z]|[a-zA-Z]+[*=']?)(?:\[.*?\])?{.*?}", 
                            help="the regex to identify latex tags").tag(config=True)
    bibformat = traits.Unicode("{author}, {year}.",
                            help=r"the format to output \cite{} tags found in the bibliography").tag(config=True)
    labelbycolon = traits.Bool(True,help=r'create reference label based on text before colon, e.g. \ref{fig:example} -> fig 1')
    
    def __init__(self, *args, **kwargs):
        # a dictionary to keep track of references, so they each get a different number
        self.refs = {}  
        # bibliography references
        self.bibdatabase = {} 
        super(LatexTagsToHTML, self).__init__( *args, **kwargs)
             
    def read_bibliography(self, path):
        """ read a bibliography
        
        """
        logging.info('reading bibliopath: {}'.format(path))
        try:
            with open(path) as bibtex_file:
                self.bibdatabase = bibtexparser.load(bibtex_file).entries_dict 
        except:
            logging.error('could not read bibliopath: {}'.format(path))
               

    def rreplace(self, source, target, replacement, replacements=1):
        """replace in string, from right-to-left"""
        return replacement.join(source.rsplit(target, replacements))
    
    def process_bib_entry(self,entry):
        """work out the best way to represent the bib entry """
        
        # abbreviate a list of authors 
        if 'author' in entry:
            authors = re.split(", | and ",entry['author'])
            if len(authors) > 1:
                author = authors[0] + ' <em>et al</em>'
            else:
                author = authors[0]
            entry['author'] = author   
        
        # split up date into year, month, day
        if 'date' in entry:
            date = entry['date'].split('-')
            if len(date) == 3:
                entry['year'] = date[0]
                entry['month'] = date[1]
                entry['day'] = date[2]
            else:
                entry['year'] = date[0]                
        
        text = DefaultFormatter().format(self.bibformat, **entry)
        
        if 'doi' in entry:
            return r'<a href="https://doi.org/{doi}">{text}</a>'.format(doi=entry['doi'], text=text)        
        elif 'url' in entry:
            return r'<a href="{url}">{text}</a>'.format(doi=entry['url'], text=text) 
        else:
            return text       
                
    def replace_reflabel(self,name,resources):
        """ find a suitable html replacement for a reference label
        
        the links are left with a format hook in them: {id_home_prefix}, 
        so that an nbconvert filter can later replace it
        this is particularly useful for slides, which require a prefix #/<slide_number><label>
        """
        if 'refmap' in resources:
            if name in resources['refmap']:
                return r'<a href="{{id_home_prefix}}{0}">{1}</a>'.format(name,resources['refmap'][name])
                
        if self.labelbycolon:
            ref_name = name.split(':')[0] if ':' in name else 'ref'
        else:
            ref_name = 'ref'
        if not ref_name in self.refs:
            self.refs[ref_name] = {}
        refs = self.refs[ref_name]
        if name in refs:
            id = refs[name]
        else:
            id = len(refs) + 1
            refs[name] = id
        return r'<a href="{{id_home_prefix}}{0}">{1}. {2}</a>'.format(name,ref_name,id)
        
    def convert(self, source, resources):
        """ convert a a string with tags in
        
        Example
        -------

        >>> source = r'''
        ... References to \\cref{fig:example}, \\cref{tbl:example}, \\cref{eqn:example_sympy} and \\cref{code:example_mpl}.
        ... 
        ... Referencing multiple items: \\cref{fig:example,fig:example_h,fig:example_v}.
        ... 
        ... An unknown latex tag.\\unknown{zelenyak_molecular_2016}
        ... '''        
        >>> processor = LatexTagsToHTML()
        >>> print(processor.convert(source,{}))
        <BLANKLINE>
        References to <a href="{id_home_prefix}fig:example">fig. 1</a>, <a href="{id_home_prefix}tbl:example">tbl. 1</a>, <a href="{id_home_prefix}eqn:example_sympy">eqn. 1</a> and <a href="{id_home_prefix}code:example_mpl">code. 1</a>.
        <BLANKLINE>
        Referencing multiple items: <a href="{id_home_prefix}fig:example">fig. 1</a>, <a href="{id_home_prefix}fig:example_h">fig. 2</a> and <a href="{id_home_prefix}fig:example_v">fig. 3</a>.
        <BLANKLINE>
        An unknown latex tag.
        <BLANKLINE>
        
        """        
        new = source           
        for tag in re.findall(self.regex, source):
            
            if tag.startswith('\\label'):
                new = new.replace(tag, r'<a id="{label}" class="anchor-link" name="#{label}">&#182;</a>'.format(label=tag[7:-1]))

            elif tag.startswith('\\ref'):
                names = tag[5:-1].split(',')
                html = []
                for name in names:
                    html.append(self.replace_reflabel(name,resources))
                new = new.replace(tag, self.rreplace(', '.join(html),',',' and'))

            elif tag.startswith('\\cref'):
                names = tag[6:-1].split(',')
                html = []
                for name in names:
                    html.append(self.replace_reflabel(name,resources))
                new = new.replace(tag, self.rreplace(', '.join(html),',',' and'))

            elif tag.startswith('\\cite'):
                names = tag[6:-1].split(',')
                html = []
                for name in names:
                    if name in self.bibdatabase:
                        html.append(self.process_bib_entry(self.bibdatabase[name]))
                    else:
                        html.append('Unresolved citation: {}.'.format(name))                    
                new = new.replace(tag, '['+', '.join(html)+']')

            else:
                new = new.replace(tag, '')
        return new
        
    def preprocess(self, nb, resources):
                
        logging.info('converting latex tags to html')
        if resources['bibliopath']:            
            self.read_bibliography(resources['bibliopath'])
            
        for cell in nb.cells:
            
            if "latex_doc" in cell['metadata']:
                for key in cell['metadata']["latex_doc"]:
                    if not isinstance(key,dict):
                        continue
                    if "caption" in cell['metadata']["latex_doc"][key]:
                        text = cell['metadata']["latex_doc"][key]["caption"]
                        cell['metadata']["latex_doc"][key]["caption"] = self.convert(text,resources)
                
            if not cell['cell_type'] == "markdown":
                continue         
            cell['source'] = self.convert(cell['source'],resources) 

        resources['refslide'] = {}
        return nb, resources