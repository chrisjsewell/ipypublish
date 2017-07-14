tplx_dict = { 
'meta_docstring':'with the main ipypublish title and contents page setup',

'document_title':r"""

((*- if nb.metadata["latex_doc"]: -*))    

  ((*- if nb.metadata["latex_doc"]["titlepage"]: -*))

	\begin{titlepage}
		
	((*- if nb.metadata["latex_doc"]["titlepage"]["logo"]: -*))
    ((* set filename = nb.metadata.latex_doc.titlepage.logo | posix_path *))
	\begin{flushright}
		\includegraphics[width=0.7\textwidth]{((( filename )))}
	\end{flushright}
	((*- endif *))

	\begin{center}

	\vspace*{1cm}
        
	\Huge
	((*- if nb.metadata["latex_doc"]["titlepage"]["title"]: -*))
	\textbf{((( nb.metadata["latex_doc"]["titlepage"]["title"] )))}
	((*- else -*))
	\textbf{((( resources.metadata.name | escape_latex )))}
	((*- endif *))

	\vspace{0.5cm}

	((*- if nb.metadata["latex_doc"]["titlepage"]["subtitle"]: -*))
	\LARGE{((( nb.metadata["latex_doc"]["titlepage"]["subtitle"] )))}
	((*- endif *))
        
	\vspace{1.5cm}

	\begin{minipage}{0.8\textwidth}   
		\begin{center}  
		\begin{minipage}{0.39\textwidth}
		\begin{flushleft} \Large
		\emph{Author:}\\
			((*- if nb.metadata["latex_doc"]["titlepage"]["author"]: -*))
			((( nb.metadata["latex_doc"]["titlepage"]["author"] )))\\
			((*- endif *))
			((*- if nb.metadata["latex_doc"]["titlepage"]["email"]: -*))
			\href{mailto:((( nb.metadata["latex_doc"]["titlepage"]["email"] )))}{((( nb.metadata["latex_doc"]["titlepage"]["email"] )))}
			((*- endif *))
		\end{flushleft}
		\end{minipage}
		\hspace{\fill}
		\begin{minipage}{0.39\textwidth}
		\begin{flushright} \Large
			((*- if nb.metadata["latex_doc"]["titlepage"]["supervisors"]: -*))
			\emph{Supervisors:} \\
			((*- for i in nb.metadata["latex_doc"]["titlepage"]["supervisors"] *))
			  ((( nb.metadata["latex_doc"]["titlepage"]["supervisors"][loop.index-1] )))
			((*- endfor *))
			((*- endif *))
		\end{flushright}
		\end{minipage}
		\end{center}   
	\end{minipage}

	\vfill

	\begin{minipage}{0.8\textwidth}
	\begin{center}  
	((*- if nb.metadata["latex_doc"]["titlepage"]["tagline"]: -*))
	\LARGE{((( nb.metadata["latex_doc"]["titlepage"]["tagline"] )))}
	((*- endif *))
	\end{center} 
	\end{minipage}
        
	\vspace{0.8cm}
        
	((*- if nb.metadata["latex_doc"]["titlepage"]["institution"]: -*))
		((*- for i in nb.metadata["latex_doc"]["titlepage"]["supervisors"] *))
		  \LARGE{((( nb.metadata["latex_doc"]["titlepage"]["institution"][loop.index-1] )))}\\
		((*- endfor *))
	((*- endif *))

	\vspace{0.4cm}

	\today
        
	\end{center}
	\end{titlepage}	

 ((*- else -*))
 
	\title{((( resources.metadata.name | escape_latex )))}
	\date{\today}
	\maketitle	
	
 ((*- endif *))

((*- endif *))

""",

'document_predoc':r"""
((*- if nb.metadata["latex_doc"]: -*))
    \begingroup
    \let\cleardoublepage\relax
    \let\clearpage\relax
    ((*- if nb.metadata["latex_doc"]["toc"]: -*))
    \tableofcontents
    ((*- endif *))
    ((*- if nb.metadata["latex_doc"]["listfigures"]: -*))
    \listoffigures
    ((*- endif *))
    ((*- if nb.metadata["latex_doc"]["listtables"]: -*))
    \listoftables
    ((*- endif *))
    ((*- if nb.metadata["latex_doc"]["listcode"]: -*))
    \listof{codecell}{List of Code}
    ((*- endif *))
    \endgroup
((*- endif *))
"""

}