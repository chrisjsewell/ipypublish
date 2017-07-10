tplx_dict = { 
'meta_docstring':'with the main ipypublish content',

'notebook_input_markdown':r"""
((*- if cell.metadata.latex_ignore: -*))
((*- elif cell.metadata.latex_caption: -*))
    \newcommand{\ky(((cell.metadata.latex_caption | create_key)))}{(((cell.source | first_para)))}
((*- else -*))	
    ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex'))))
((*- endif *))
""",

'notebook_output':r"""
((*- if cell.metadata.latex_ignore: -*))
((*- else -*))	
((( super() )))
((*- endif *))
""",

'notebook_output_stream':r"""
((( super() )))
""",

'notebook_output_latex':r"""
((*- if cell.metadata.latex_table: -*))
    ((*- if cell.metadata.latex_table.placement: -*))
    \begin{table}[(((cell.metadata.latex_table.placement)))]
    ((*- else -*))	
    \begin{table}
    ((*- endif *))
    
    ((* set ckey = cell.metadata.latex_table.label | create_key *))
	\ifdefined\ky((( ckey )))
	 \caption{\ky((( ckey )))}
	\else
	 \caption{((( cell.metadata.latex_table.caption )))}
	\fi
    \label{((( cell.metadata.latex_table.label )))}
    
    \centering
    ((*- if cell.metadata.latex_table.alternate: -*))
    \rowcolors{2}{(((cell.metadata.latex_table.alternate)))}{white}
    ((*- endif *))
    ((( output.data['text/latex'] )))
    \end{table}
    
((*- elif cell.metadata.latex_equation: -*))

	((*- if cell.metadata.latex_equation.label: -*))
    \begin{equation}\label{((( cell.metadata.latex_equation.label )))}
	((*- else -*))	
    \begin{equation}
	((*- endif *))	
	((( output.data['text/latex'] | remove_dollars )))
    \end{equation}
    
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
((*- if meta.latex_figure: -*))
((* set filename = filename | posix_path *))
((*- block figure scoped -*))

    ((*- if meta.latex_figure.placement: -*))
        ((*- if meta.latex_figure.widefigure: -*))
    \begin{figure*}[(((meta.latex_figure.placement)))]
        ((*- else -*))
    \begin{figure}[(((meta.latex_figure.placement)))]
        ((*- endif *))
    ((*- else -*))
        ((*- if meta.latex_figure.widefigure: -*))
    \begin{figure*}
        ((*- else -*))
    \begin{figure}
        ((*- endif *))
    ((*- endif *))
        \begin{center}\adjustimage{max size={0.9\linewidth}{0.4\paperheight}}{((( filename )))}\end{center}

        ((* set ckey = meta.latex_figure.label | create_key *))
		\ifdefined\ky((( ckey )))
		 \caption{\ky((( ckey )))}
		\else
		 \caption{ ((( meta.latex_figure.caption ))) }
		\fi
        \label{ ((( meta.latex_figure.label ))) }
    \end{figure}

((*- endblock figure -*))
((*- endif *))
((*- endmacro *))
"""

}

