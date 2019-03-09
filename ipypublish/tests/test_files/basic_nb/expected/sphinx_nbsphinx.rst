

a title
=======

some text

.. nbinput:: ipython3
    :execution-count: 2

    a=1
    print(a)

.. nboutput:: ansi

    .. rst-class:: highlight

    .. raw:: html

        <pre>
        1
        </pre>

    .. raw:: latex

        %
        {
        \kern-\sphinxverbatimsmallskipamount\kern-\baselineskip
        \kern+\FrameHeightAdjust\kern-\fboxrule
        \vspace{\nbsphinxcodecellspacing}
        \sphinxsetup{VerbatimBorderColor={named}{nbsphinx-code-border}}
        \sphinxsetup{VerbatimColor={named}{white}}
        \fvset{hllines={, ,}}%
        \begin{sphinxVerbatim}[commandchars=\\\{\}]
        1
        \end{sphinxVerbatim}
        }
        % The following \relax is needed to avoid problems with adjacent ANSI
        % cells and some other stuff (e.g. bullet lists) following ANSI cells.
        % See https://github.com/sphinx-doc/sphinx/issues/3594
        \relax
