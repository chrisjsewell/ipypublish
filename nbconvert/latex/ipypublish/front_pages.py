tplx_dict = { 
'meta_docstring':'with the main ipypublish title and contents page setup',

'document_title':r"""

  ((*- if nb.metadata["latex_metadata"]: -*))

	\begin{titlepage}
		
	((*- if nb.metadata["latex_metadata"]["logo"]: -*))
	\begin{flushright}
		\includegraphics{((( nb.metadata["latex_metadata"]["logo"] )))}
	\end{flushright}
	((*- endif *))

	\begin{center}

	\vspace*{1cm}
        
	\Huge
	((*- if nb.metadata["latex_metadata"]["title"]: -*))
	\textbf{((( nb.metadata["latex_metadata"]["title"] )))}
	((*- else -*))
	\textbf{((( resources.metadata.name | escape_latex )))}
	((*- endif *))

	\vspace{0.5cm}

	((*- if nb.metadata["latex_metadata"]["subtitle"]: -*))
	\LARGE{((( nb.metadata["latex_metadata"]["subtitle"] )))}
	((*- endif *))
        
	\vspace{1.5cm}

	\begin{minipage}{0.8\textwidth}   
		\begin{center}  
		\begin{minipage}{0.39\textwidth}
		\begin{flushleft} \Large
		\emph{Author:}\\
			((*- if nb.metadata["latex_metadata"]["author"]: -*))
			((( nb.metadata["latex_metadata"]["author"] )))\\
			((*- endif *))
			((*- if nb.metadata["latex_metadata"]["email"]: -*))
			\href{mailto:((( nb.metadata["latex_metadata"]["email"] )))}{((( nb.metadata["latex_metadata"]["email"] )))}
			((*- endif *))
		\end{flushleft}
		\end{minipage}
		\hspace{\fill}
		\begin{minipage}{0.39\textwidth}
		\begin{flushright} \Large
			((*- if nb.metadata["latex_metadata"]["supervisors"]: -*))
			\emph{Supervisors:} \\
			((*- for i in nb.metadata["latex_metadata"]["supervisors"] *))
			  ((( nb.metadata["latex_metadata"]["supervisors"][loop.index-1] )))
			((*- endfor *))
			((*- endif *))
		\end{flushright}
		\end{minipage}
		\end{center}   
	\end{minipage}

	\vfill

	\begin{minipage}{0.8\textwidth}
	\begin{center}  
	((*- if nb.metadata["latex_metadata"]["tagline"]: -*))
	\LARGE{((( nb.metadata["latex_metadata"]["tagline"] )))}
	((*- endif *))
	\end{center} 
	\end{minipage}
        
	\vspace{0.8cm}
        
	((*- if nb.metadata["latex_metadata"]["institution"]: -*))
		((*- for i in nb.metadata["latex_metadata"]["supervisors"] *))
		  \LARGE{((( nb.metadata["latex_metadata"]["institution"][loop.index-1] )))}\\
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

""",

'document_predoc':r'\tableofcontents'

}