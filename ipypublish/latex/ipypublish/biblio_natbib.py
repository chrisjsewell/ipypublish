tplx_dict = { 
'meta_docstring':'with the main ipypublish bibliography',

'document_packages':r"""
	% bibliography formatting
	\usepackage[numbers, square, super, sort&compress]{natbib}
	% hyperlink doi's
	\usepackage{doi}	
""",

'document_bibliography':r"""
((*- if nb.metadata.latex_doc: -*))
((*- if nb.metadata.latex_doc.bibliography: -*))
((* set filename = nb.metadata.latex_doc.bibliography | posix_path *))

% sort citations by order of first appearance
\bibliographystyle{unsrtnat}
\bibliography{((( filename )))}

((*- endif *))
((*- endif *))
"""

}