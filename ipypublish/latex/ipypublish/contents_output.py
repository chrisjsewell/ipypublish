tplx_dict = { 
'meta_docstring':'with the main ipypublish content',

'notebook_input':r"""
((*- if cell.metadata.latex_doc: -*))
    ((*- if cell.metadata.latex_doc.ignore: -*))
    ((*- else -*))	
    ((( super() )))
    ((*- endif *))
((*- else -*))	
    ((( super() )))
((*- endif *))
""",

'notebook_input_markdown':r"""
((*- if cell.metadata.latex_doc: -*))
    ((*- if cell.metadata.latex_doc.caption: -*))
        \newcommand{\ky(((cell.metadata.latex_doc.caption | create_key)))}{(((cell.source | first_para)))}
    ((*- else -*))	
        ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex'))))
    ((*- endif *))
((*- else -*))	
    ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex'))))
((*- endif *))

""",

'notebook_output':r"""
((*- if cell.metadata.latex_doc: -*))
    ((*- if cell.metadata.latex_doc.ignore: -*))
    ((*- else -*))	
    ((( super() )))
    ((*- endif *))
((*- else -*))	
    ((( super() )))
((*- endif *))
""",

'notebook_output_stream':r"""
((*- if cell.metadata.latex_doc: -*))
    ((*- if cell.metadata.latex_doc.ignore: -*))
    ((*- else -*))	
    ((( super() )))
    ((*- endif *))
((*- else -*))	
    ((( super() )))
((*- endif *))
""",

'notebook_output_latex':r"""
((*- if cell.metadata.latex_doc: -*))
    ((*- if cell.metadata.latex_doc.table: -*))
        ((*- if cell.metadata.latex_doc.table.placement: -*))
        \begin{table}[(((cell.metadata.latex_doc.table.placement)))]
        ((*- else -*))	
        \begin{table}
        ((*- endif *))
    
        ((* set ckey = cell.metadata.latex_doc.table.label | create_key *))
    	\ifdefined\ky((( ckey )))
    	 \caption{\ky((( ckey )))}
    	\else
    	 \caption{((( cell.metadata.latex_doc.table.caption )))}
    	\fi
        \label{((( cell.metadata.latex_doc.table.label )))}
    
        \centering
        ((*- if cell.metadata.latex_doc.table.alternate: -*))
        \rowcolors{2}{(((cell.metadata.latex_doc.table.alternate)))}{white}
        ((*- endif *))
        ((( output.data['text/latex'] )))
        \end{table}
    
    ((*- elif cell.metadata.latex_doc.equation: -*))

    	((*- if cell.metadata.latex_doc.equation.label: -*))
        \begin{equation}\label{((( cell.metadata.latex_doc.equation.label )))}
    	((*- else -*))	
        \begin{equation}
    	((*- endif *))	
    	((( output.data['text/latex'] | remove_dollars )))
        \end{equation}
    
    ((*- elif cell.metadata.latex_doc.caption: -*))

        \newcommand{\ky(((cell.metadata.latex_doc.caption | create_key)))}{(((output.data['text/latex'] | first_para)))}

    ((*- endif *))
((*- endif *))
""",


#'notebook_output_markdown':'',
'notebook_output_png':r"""
((( draw_figure(output.metadata.filenames['image/png'],
cell.metadata) )))

""",
'notebook_output_jpg':r"""
((( draw_figure(output.metadata.filenames['image/jpeg'],
cell.metadata) )))

""",
'notebook_output_svg':r"""
((( draw_figure(output.metadata.filenames['image/svg+xml'],
cell.metadata) )))

""",
'notebook_output_pdf':r"""
((( draw_figure(output.metadata.filenames['application/pdf'],
cell.metadata) )))

""",

'jinja_macros':r"""
((* macro draw_figure(filename, meta) -*))
((*- if meta.latex_doc: -*))
((*- if meta.latex_doc.figure: -*))
((* set filename = filename | posix_path *))
((*- block figure scoped -*))

    ((*- if meta.latex_doc.figure.placement: -*))
        ((*- if meta.latex_doc.figure.widefigure: -*))
    \begin{figure*}[(((meta.latex_doc.figure.placement)))]
        ((*- else -*))
    \begin{figure}[(((meta.latex_doc.figure.placement)))]
        ((*- endif *))
    ((*- else -*))
        ((*- if meta.latex_doc.figure.widefigure: -*))
    \begin{figure*}
        ((*- else -*))
    \begin{figure}
        ((*- endif *))
    ((*- endif *))
        \begin{center}\adjustimage{max size={0.9\linewidth}{0.4\paperheight}}{((( filename )))}\end{center}

        ((* set ckey = meta.latex_doc.figure.label | create_key *))
		\ifdefined\ky((( ckey )))
		 \caption{\ky((( ckey )))}
		\else
		 \caption{((( meta.latex_doc.figure.caption )))}
		\fi
        \label{((( meta.latex_doc.figure.label )))}
    \end{figure}

((*- endblock figure -*))
((*- endif *))
((*- endif *))
((*- endmacro *))
"""

}

