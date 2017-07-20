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
((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex'))))
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
    
        ((*- if resources.captions and cell.metadata.latex_doc.table.label -*))
            ((*- if resources.captions[cell.metadata.latex_doc.table.label]: -*))
             \caption{((( resources.captions[cell.metadata.latex_doc.table.label] )))}
            ((*- elif cell.metadata.latex_doc.table.caption -*))   
             \caption{((( cell.metadata.latex_doc.table.caption )))}
            ((*- endif *))
        ((*- elif cell.metadata.latex_doc.table.caption -*))
         \caption{((( cell.metadata.latex_doc.table.caption )))}
        ((*- endif *))

        ((*- if cell.metadata.latex_doc.table.label -*))
        \label{((( cell.metadata.latex_doc.table.label )))}
        ((*- endif *))
    
        \centering
        ((*- if cell.metadata.latex_doc.table.alternate: -*))
        \rowcolors{2}{(((cell.metadata.latex_doc.table.alternate)))}{white}
        ((*- endif *))
        ((( output.data['text/latex'] )))
        \end{table}
    
    ((*- elif "equation" in cell.metadata.latex_doc: -*))

    	((*- if cell.metadata.latex_doc.equation.label: -*))
        \begin{equation}\label{((( cell.metadata.latex_doc.equation.label )))}
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

        ((*- if resources.captions: -*))
            ((*- if resources.captions[meta.latex_doc.figure.label]: -*))
             \caption{((( resources.captions[meta.latex_doc.figure.label] )))}
            ((*- else -*))   
             \caption{((( meta.latex_doc.figure.caption )))}
            ((*- endif *))
        ((*- elif meta.latex_doc.figure.caption: -*))
             \caption{((( meta.latex_doc.figure.caption )))}
        ((*- endif *))
        ((*- if meta.latex_doc.figure.label: -*))
        \label{((( meta.latex_doc.figure.label )))}
        ((*- endif *))
    \end{figure}

((*- endblock figure -*))
((*- endif *))
((*- endif *))
((*- endmacro *))
"""

}

