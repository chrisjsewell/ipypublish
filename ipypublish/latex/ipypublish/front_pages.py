tplx_dict = { 
'meta_docstring':'with the main ipypublish title and contents page setup',

'document_title':r"""

((*- if nb.metadata["ipub"]: -*))    

  ((*- if nb.metadata["ipub"]["titlepage"]: -*))

	\begin{titlepage}
		
	((*- if nb.metadata["ipub"]["titlepage"]["logo"]: -*))
    ((* set filename = nb.metadata.ipub.titlepage.logo | posix_path *))
	\begin{flushright}
		\includegraphics[width=0.7\textwidth]{((( filename )))}
	\end{flushright}
	((*- endif *))

	\begin{center}

	\vspace*{1cm}
        
	\Huge
	((*- if nb.metadata["ipub"]["titlepage"]["title"]: -*))
	\textbf{((( nb.metadata["ipub"]["titlepage"]["title"] )))}
	((*- else -*))
	\textbf{((( resources.metadata.name | escape_latex )))}
	((*- endif *))

	\vspace{0.5cm}

	((*- if nb.metadata["ipub"]["titlepage"]["subtitle"]: -*))
	\LARGE{((( nb.metadata["ipub"]["titlepage"]["subtitle"] )))}
	((*- endif *))
        
	\vspace{1.5cm}

	\begin{minipage}{0.8\textwidth}   
		\begin{center}  
		\begin{minipage}{0.39\textwidth}
		\begin{flushleft} \Large
		\emph{Author:}\\
			((*- if nb.metadata["ipub"]["titlepage"]["author"]: -*))
			((( nb.metadata["ipub"]["titlepage"]["author"] )))\\
			((*- endif *))
			((*- if nb.metadata["ipub"]["titlepage"]["email"]: -*))
			\href{mailto:((( nb.metadata["ipub"]["titlepage"]["email"] )))}{((( nb.metadata["ipub"]["titlepage"]["email"] )))}
			((*- endif *))
		\end{flushleft}
		\end{minipage}
		\hspace{\fill}
		\begin{minipage}{0.39\textwidth}
		\begin{flushright} \Large
			((*- if nb.metadata["ipub"]["titlepage"]["supervisors"]: -*))
			\emph{Supervisors:} \\
			((*- for i in nb.metadata["ipub"]["titlepage"]["supervisors"] *))
			  ((( nb.metadata["ipub"]["titlepage"]["supervisors"][loop.index-1] )))
			((*- endfor *))
			((*- endif *))
		\end{flushright}
		\end{minipage}
		\end{center}   
	\end{minipage}

	\vfill

	\begin{minipage}{0.8\textwidth}
	\begin{center}  
	((*- if nb.metadata["ipub"]["titlepage"]["tagline"]: -*))
	\LARGE{((( nb.metadata["ipub"]["titlepage"]["tagline"] )))}
	((*- endif *))
	\end{center} 
	\end{minipage}
        
	\vspace{0.8cm}
        
	((*- if nb.metadata["ipub"]["titlepage"]["institution"]: -*))
		((*- for i in nb.metadata["ipub"]["titlepage"]["supervisors"] *))
		  \LARGE{((( nb.metadata["ipub"]["titlepage"]["institution"][loop.index-1] )))}\\
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
((*- if nb.metadata["ipub"]: -*))
    \begingroup
    \let\cleardoublepage\relax
    \let\clearpage\relax
    ((*- if nb.metadata["ipub"]["toc"]: -*))
    \tableofcontents
    ((*- endif *))
    ((*- if nb.metadata["ipub"]["listfigures"]: -*))
    \listoffigures
    ((*- endif *))
    ((*- if nb.metadata["ipub"]["listtables"]: -*))
    \listoftables
    ((*- endif *))
    ((*- if nb.metadata["ipub"]["listcode"]: -*))
    \listof{codecell}{List of Code}
    ((*- endif *))
    \endgroup
((*- endif *))
"""

}