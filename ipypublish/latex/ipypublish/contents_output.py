tplx_dict = { 
'meta_docstring':'with the main ipypublish content',

'notebook_input':r"""
((*- if cell.metadata.ipub: -*))
    ((*- if cell.metadata.ipub.ignore: -*))
    ((*- elif cell.metadata.ipub.slideonly: -*))
    ((*- else -*))	
    ((( super() )))
    ((*- endif *))
((*- else -*))	
    ((( super() )))
((*- endif *))
""",

'notebook_input_markdown':r"""
((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex'))))
""",

'notebook_output':r"""
((*- if cell.metadata.ipub: -*))
    ((*- if cell.metadata.ipub.ignore: -*))
    ((*- elif cell.metadata.ipub.slideonly: -*))
    ((*- else -*))	
    ((( super() )))
    ((*- endif *))
((*- else -*))	
    ((( super() )))
((*- endif *))
""",

'notebook_output_markdown':"""
((*- if cell.metadata.ipub: -*))
    ((*- if cell.metadata.ipub.mkdown: -*))
((( output.data['text/markdown'] | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex'))))
((*- endif *))
((*- endif *))
""",

'notebook_output_stream':r"""
((*- if cell.metadata.ipub: -*))
    ((*- if cell.metadata.ipub.ignore: -*))
    ((*- else -*))	
    ((( super() )))
    ((*- endif *))
((*- else -*))	
    ((( super() )))
((*- endif *))
""",

'notebook_output_latex':r"""
((*- if cell.metadata.ipub: -*))
    ((*- if cell.metadata.ipub.table: -*))
        ((*- if cell.metadata.ipub.table.placement: -*))
        \begin{table}[(((cell.metadata.ipub.table.placement)))]
        ((*- else -*))	
        \begin{table}
        ((*- endif *))
    
        ((*- if resources.captions and cell.metadata.ipub.table.label -*))
            ((*- if resources.captions[cell.metadata.ipub.table.label]: -*))
             \caption{((( resources.captions[cell.metadata.ipub.table.label] )))}
            ((*- elif cell.metadata.ipub.table.caption -*))   
             \caption{((( cell.metadata.ipub.table.caption )))}
            ((*- endif *))
        ((*- elif cell.metadata.ipub.table.caption -*))
         \caption{((( cell.metadata.ipub.table.caption )))}
        ((*- endif *))

        ((*- if cell.metadata.ipub.table.label -*))
        \label{((( cell.metadata.ipub.table.label )))}
        ((*- endif *))
    
        \centering
		\begin{adjustbox}{max width=\textwidth}
        ((*- if cell.metadata.ipub.table.alternate: -*))
        \rowcolors{2}{(((cell.metadata.ipub.table.alternate)))}{white}
        ((*- endif *))
        ((( output.data['text/latex'] )))
		\end{adjustbox}
        \end{table}
    
    ((*- elif "equation" in cell.metadata.ipub: -*))

    	((*- if cell.metadata.ipub.equation.label: -*))
        \begin{equation}\label{((( cell.metadata.ipub.equation.label )))}
    	((*- else -*))	
        \begin{equation}
    	((*- endif *))	
    	((( output.data['text/latex'] | remove_dollars )))
        \end{equation}
    
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
((*- if meta.ipub: -*))
((*- if meta.ipub.figure: -*))
((* set filename = filename | posix_path *))
((*- block figure scoped -*))

    ((*- if meta.ipub.figure.placement: -*))
        ((*- if meta.ipub.figure.widefigure: -*))
    \begin{figure*}[(((meta.ipub.figure.placement)))]
        ((*- else -*))
    \begin{figure}[(((meta.ipub.figure.placement)))]
        ((*- endif *))
    ((*- else -*))
        ((*- if meta.ipub.figure.widefigure: -*))
    \begin{figure*}
        ((*- else -*))
    \begin{figure}
        ((*- endif *))
    ((*- endif *))
        ((*- if meta.ipub.figure.width: -*))
        \begin{center}\adjustimage{max size={0.9\linewidth}{0.9\paperheight},width=(((meta.ipub.figure.width)))\linewidth}{((( filename )))}\end{center}
        ((*- elif meta.ipub.figure.height: -*))
        \begin{center}\adjustimage{max size={0.9\linewidth}{0.9\paperheight},height=(((meta.ipub.figure.height)))\paperheight}{((( filename )))}\end{center}
        ((*- else -*))
        \begin{center}\adjustimage{max size={0.9\linewidth}{0.9\paperheight}}{((( filename )))}\end{center}
        ((*- endif *))

        ((*- if resources.captions: -*))
            ((*- if resources.captions[meta.ipub.figure.label]: -*))
             \caption{((( resources.captions[meta.ipub.figure.label] )))}
            ((*- else -*))   
             \caption{((( meta.ipub.figure.caption )))}
            ((*- endif *))
        ((*- elif meta.ipub.figure.caption: -*))
             \caption{((( meta.ipub.figure.caption )))}
        ((*- endif *))
        ((*- if meta.ipub.figure.label: -*))
        \label{((( meta.ipub.figure.label )))}
        ((*- endif *))
    \end{figure}

((*- endblock figure -*))
((*- endif *))
((*- endif *))
((*- endmacro *))
"""

}

