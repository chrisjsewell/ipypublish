tplx_dict = { 
'meta_docstring':'with the input code wrapped and framed',

'document_packages':r"""

    % define a code float
    \usepackage{newfloat} % to define a new float types
    \DeclareFloatingEnvironment[
        fileext=frm,placement={!ht},
        within=section,name=Code]{codecell}
        
    \usepackage{listings} % a package for wrapping code in a box
    \usepackage[framemethod=tikz]{mdframed} % to fram code

""",

'document_header_end':r"""
% make the code float work with cleverref
\crefname{codecell}{code}{codes}
\Crefname{codecell}{code}{codes}
""",

'document_definitions':r"""
\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.95}

\lstdefinestyle{mystyle}{
    commentstyle=\color{codegreen},
    keywordstyle=\color{magenta},
    numberstyle=\tiny\color{codegray},
    stringstyle=\color{codepurple},
    basicstyle=\ttfamily,
    breakatwhitespace=false,         
    keepspaces=true,                 
    numbers=left,                    
    numbersep=10pt,                  
    showspaces=false,                
    showstringspaces=false,
    showtabs=false,                  
    tabsize=2,
  breaklines=true,
  postbreak=\mbox{\textcolor{red}{$\hookrightarrow$}\space},
}
 
\lstset{style=mystyle} 

\surroundwithmdframed[
  hidealllines=true,
  backgroundcolor=backcolour,
  innerleftmargin=20pt,
  innertopmargin=2pt,
  innerbottommargin=0pt]{lstlisting}

""",

'notebook_input':r"""
((*- if cell.metadata.latex_doc: -*))

((*- if cell.metadata.latex_doc.code: -*))

((*- if cell.metadata.latex_doc.code.asfloat: -*))
    ((*- if cell.metadata.latex_doc.code.placement: -*))
        ((*- if cell.metadata.latex_doc.code.widefigure: -*))
    \begin{codecell*}[((cell.metadata.latex_doc.code.placement)))]
        ((*- else -*))
    \begin{codecell}[(((cell.metadata.latex_doc.code.placement)))]
        ((*- endif *))
    ((*- else -*))
        ((*- if cell.metadata.latex_doc.code.widefigure: -*))
    \begin{codecell*}
        ((*- else -*))
    \begin{codecell}
        ((*- endif *))
    ((*- endif *))

    ((*- if cell.metadata.latex_doc.code.label: -*))
        ((* set ckey = cell.metadata.latex_doc.code.label | create_key *))
        \ifdefined\ky((( ckey )))
         \caption{\ky((( ckey )))}
        \else
         ((*- if cell.metadata.latex_doc.code.caption: -*))
         \caption{((( cell.metadata.latex_doc.code.caption )))}
         ((*- endif *))
        \fi
    ((*- elif cell.metadata.latex_doc.code.caption: -*))
    \caption{((( cell.metadata.latex_doc.code.caption )))}
    ((*- endif *))
((*- endif *))

((*- if cell.metadata.latex_doc.code.label: -*))
\label{((( cell.metadata.latex_doc.code.label )))}
((*- endif *))

\begin{lstlisting}[language=Python]
((( cell.source )))
\end{lstlisting}

((*- if cell.metadata.latex_doc.code.asfloat: -*))
\end{codecell}
((*- endif *))

((*- endif *))

((*- endif *))
""",

'jinja_macros':r"""
"""

}

