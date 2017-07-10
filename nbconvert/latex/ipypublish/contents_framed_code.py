tplx_dict = { 
'meta_docstring':'with the input code wrapped and framed',

'document_packages':r"""
	% For framing 
    \usepackage{tikz} % Needed to box output/input
    \usepackage{scrextend} % Used to indent output
    \usepackage{needspace} % Make prompts follow contents
    \usepackage{framed} % Used to draw output that spans multiple pages
""",

'document_definitions':r"""
    % NB prompt colors
    \definecolor{nbframe-border}{rgb}{0.867,0.867,0.867}
    \definecolor{nbframe-bg}{rgb}{0.969,0.969,0.969}
    \definecolor{nbframe-in-prompt}{rgb}{0.0,0.0,0.502}
    \definecolor{nbframe-out-prompt}{rgb}{0.545,0.0,0.0}

    % NB prompt lengths
    \newlength{\inputpadding}
    \setlength{\inputpadding}{0.5em}
    \newlength{\cellleftmargin} % distance from left of page
    \setlength{\cellleftmargin}{1pt}
    \newlength{\borderthickness}
    \setlength{\borderthickness}{0.4pt}
    \newlength{\smallerfontscale}
    \setlength{\smallerfontscale}{9pt}

    % NB prompt font size
    \def\smaller{\fontsize{\smallerfontscale}{\smallerfontscale}\selectfont}

    % Define a background layer, in which the nb prompt shape is drawn
    \pgfdeclarelayer{background}
    \pgfsetlayers{background,main}
    \usetikzlibrary{calc}

    % define styles for the normal border and the torn border
    \tikzset{
      normal border/.style={draw=nbframe-border, fill=nbframe-bg,
        rectangle, rounded corners=2.5pt, line width=\borderthickness},
      torn border/.style={draw=white, fill=white, line width=\borderthickness}}

    % Macro to draw the shape behind the text, when it fits completly in the
    % page
    \def\notebookcellframe#1{%
    \tikz{%
      \node[inner sep=\inputpadding] (A) {#1};% Draw the text of the node
      \begin{pgfonlayer}{background}% Draw the shape behind
      \fill[normal border]%
            (A.south east) -- ($(A.south west)+(\cellleftmargin,0)$) -- 
            ($(A.north west)+(\cellleftmargin,0)$) -- (A.north east) -- cycle;
      \end{pgfonlayer}}}%

    % Macro to draw the shape, when the text will continue in next page
    \def\notebookcellframetop#1{%
    \tikz{%
      \node[inner sep=\inputpadding] (A) {#1};    % Draw the text of the node
      \begin{pgfonlayer}{background}    
      \fill[normal border]              % Draw the ``complete shape'' behind
            (A.south east) -- ($(A.south west)+(\cellleftmargin,0)$) -- 
            ($(A.north west)+(\cellleftmargin,0)$) -- (A.north east) -- cycle;
      \fill[torn border]                % Add the torn lower border
            ($(A.south east)-(0,.1)$) -- ($(A.south west)+(\cellleftmargin,-.1)$) -- 
            ($(A.south west)+(\cellleftmargin,.1)$) -- ($(A.south east)+(0,.1)$) -- cycle;
      \end{pgfonlayer}}}

    % Macro to draw the shape, when the text continues from previous page
    \def\notebookcellframebottom#1{%
    \tikz{%
      \node[inner sep=\inputpadding] (A) {#1};   % Draw the text of the node
      \begin{pgfonlayer}{background}   
      \fill[normal border]             % Draw the ``complete shape'' behind
            (A.south east) -- ($(A.south west)+(\cellleftmargin,0)$) -- 
            ($(A.north west)+(\cellleftmargin,0)$) -- (A.north east) -- cycle;
      \fill[torn border]               % Add the torn upper border
            ($(A.north east)-(0,.1)$) -- ($(A.north west)+(\cellleftmargin,-.1)$) -- 
            ($(A.north west)+(\cellleftmargin,.1)$) -- ($(A.north east)+(0,.1)$) -- cycle;
      \end{pgfonlayer}}}

    % Macro to draw the shape, when both the text continues from previous page
    % and it will continue in next page
    \def\notebookcellframemiddle#1{%
    \tikz{%
      \node[inner sep=\inputpadding] (A) {#1};   % Draw the text of the node
      \begin{pgfonlayer}{background}   
      \fill[normal border]             % Draw the ``complete shape'' behind
            (A.south east) -- ($(A.south west)+(\cellleftmargin,0)$) -- 
            ($(A.north west)+(\cellleftmargin,0)$) -- (A.north east) -- cycle;
      \fill[torn border]               % Add the torn lower border
            ($(A.south east)-(0,.1)$) -- ($(A.south west)+(\cellleftmargin,-.1)$) -- 
            ($(A.south west)+(\cellleftmargin,.1)$) -- ($(A.south east)+(0,.1)$) -- cycle;
      \fill[torn border]               % Add the torn upper border
            ($(A.north east)-(0,.1)$) -- ($(A.north west)+(\cellleftmargin,-.1)$) -- 
            ($(A.north west)+(\cellleftmargin,.1)$) -- ($(A.north east)+(0,.1)$) -- cycle;
      \end{pgfonlayer}}}

    % Define the environment which puts the frame
    % In this case, the environment also accepts an argument with an optional
    % title (which defaults to ``Example'', which is typeset in a box overlaid
    % on the top border
    \newenvironment{notebookcell}[1][0]{%
      \def\FrameCommand{\notebookcellframe}%
      \def\FirstFrameCommand{\notebookcellframetop}%
      \def\LastFrameCommand{\notebookcellframebottom}%
      \def\MidFrameCommand{\notebookcellframemiddle}%
      %\par\vspace{1\baselineskip}%
      \MakeFramed {\FrameRestore}%
      \noindent\tikz\node[inner sep=0em] at ($(A.north west)-(0,0)$) {%
      ((( draw_prompt("In", "#1", "nbframe-in-prompt", "2pt") )))%
      }; \par}%
    {\endMakeFramed}

""",

'notebook_input':r"""

((*- if cell.metadata.latex_code: -*))

((*- if cell.metadata.latex_code.exec_number: -*))
    ((* set exec_number = cell.execution_count *))
((*- else -*))
    ((* set exec_number = "" *))
((*- endif *))

{%\par%
%\vspace{-1\baselineskip}%
%\needspace{4\baselineskip}}%
\begin{notebookcell}[((( exec_number )))]%
\begin{addmargin}[\cellleftmargin]{0.1pt}% left, right
{\smaller%
\par%
((* block extra_input_spacing *))((* endblock extra_input_spacing *))%
\vspace{-1\smallerfontscale}%
((( cell.source | wrap_text(82) | highlight2latex )))%
\par%
\vspace{0.3\smallerfontscale}}%
\end{addmargin}
\end{notebookcell}

((*- endif *))

""",

'jinja_macros':r"""

% Purpose: Renders an output/input prompt for notebook style pdfs
((* macro draw_prompt(prompt, number, color, space) -*))
    \begin{minipage}{\cellleftmargin}%
    \hfill%
    {\smaller%
    \tt%
    \color{(((color)))}%
    (((prompt)))[(((number)))]:}%
    \hspace{\inputpadding}%
    \hspace{(((space)))}%
    \hspace{3pt}%
    \end{minipage}%
((*- endmacro *))

"""

}

