

.. nbinput:: ipython3
    :no-output:

    from ipypublish.scripts.ipynb_latex_setup import *

Markdown
========

General
-------

Some markdown text.

A list:

-  something
-  something else

A numbered list

1. something
2. something else

non-ascii characters TODO

This is a long section of text, which we only want in a document (not a presentation) some text some more text some more text some more text some more text some more text some more text some more text some more text

This is an abbreviated section of the document text, which we only want in a presentation

-  summary of document text

References and Citations
------------------------

References to :nbsphinx-math:`\cref{fig:example}`, :nbsphinx-math:`\cref{tbl:example}`, :nbsphinx-math:`\cref{eqn:example_sympy}` and :nbsphinx-math:`\cref{code:example_mpl}`.

A latex citation.:nbsphinx-math:`\cite{zelenyak_molecular_2016}`

A html citation.:cite:`kirkeminde_thermodynamic_2012`

Todo notes
----------

.. math::
   :nowrap:

   \todo[inline]{an inline todo}

Some text.:nbsphinx-math:`\todo{a todo in the margins}`

Text Output
===========

.. nbinput:: ipython3
    :execution-count: 3

    print("""
    This is some printed text,
    with a nicely formatted output.
    """)

.. nboutput:: ansi

    .. rst-class:: highlight

    .. raw:: html

        <pre>

        This is some printed text,
        with a nicely formatted output.

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

        This is some printed text,
        with a nicely formatted output.

        \end{sphinxVerbatim}
        }
        % The following \relax is needed to avoid problems with adjacent ANSI
        % cells and some other stuff (e.g. bullet lists) following ANSI cells.
        % See https://github.com/sphinx-doc/sphinx/issues/3594
        \relax

Images and Figures
==================

.. nbinput:: ipython3
    :execution-count: 3

    Image('example.jpg',height=400)

.. nboutput:: rst
    :execution-count: 3

    .. image:: output_13_0.jpeg
        :height: 400

Displaying a plot with its code
-------------------------------

A matplotlib figure, with the caption set in the markdowncell above the figure.

The plotting code for a matplotlib figure (:nbsphinx-math:`\cref{fig:example_mpl}`).

.. nbinput:: ipython3
    :execution-count: 9

    plt.scatter(np.random.rand(10), np.random.rand(10), 
                label='data label')
    plt.ylabel(r'a y label with latex $\alpha$')
    plt.legend();

.. only:: html

    .. nboutput:: rst

        .. image:: output_17_0.svg

.. only:: latex

    .. nboutput:: rst

        .. image:: output_17_0.pdf

Tables (with pandas)
====================

The plotting code for a pandas Dataframe table (:nbsphinx-math:`\cref{tbl:example}`).

.. nbinput:: ipython3
    :execution-count: 8

    df = pd.DataFrame(np.random.rand(3,4),columns=['a','b','c','d'])
    df.a = ['$\delta$','x','y']
    df.b = ['l','m','n']
    df.set_index(['a','b'])
    df.round(3)

.. only:: html

    .. nboutput:: rst
        :execution-count: 8
        :class: rendered_html

        .. raw:: html

            <div>
            <style>
                .dataframe thead tr:only-child th {
                    text-align: right;
                }

                .dataframe thead th {
                    text-align: left;
                }

                .dataframe tbody tr th {
                    vertical-align: top;
                }
            </style>
            <table border="1" class="dataframe">
              <thead>
                <tr style="text-align: right;">
                  <th></th>
                  <th>a</th>
                  <th>b</th>
                  <th>c</th>
                  <th>d</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>0</th>
                  <td>$\delta$</td>
                  <td>l</td>
                  <td>0.583</td>
                  <td>0.279</td>
                </tr>
                <tr>
                  <th>1</th>
                  <td>x</td>
                  <td>m</td>
                  <td>0.914</td>
                  <td>0.021</td>
                </tr>
                <tr>
                  <th>2</th>
                  <td>y</td>
                  <td>n</td>
                  <td>0.333</td>
                  <td>0.116</td>
                </tr>
              </tbody>
            </table>
            </div>

.. only:: latex

    .. nboutput:: rst
        :execution-count: 8

        .. math::
            :nowrap:

            \begin{tabular}{lllrr}
            \toprule
            {} &         a &  b &      c &      d \\
            \midrule
            0 &  $\delta$ &  l &  0.583 &  0.279 \\
            1 &         x &  m &  0.914 &  0.021 \\
            2 &         y &  n &  0.333 &  0.116 \\
            \bottomrule
            \end{tabular}

Equations (with ipython or sympy)
=================================

.. nbinput:: ipython3
    :execution-count: 9

    Latex('$$ a = b+c $$')

.. nboutput:: rst
    :execution-count: 9

    .. math::
        :nowrap:

        $$ a = b+c $$

The plotting code for a sympy equation (:nbsphinx-math:`\cref{eqn:example_sympy}`).

.. nbinput:: ipython3
    :execution-count: 10

    y = sym.Function('y')
    n = sym.symbols(r'\alpha')
    f = y(n)-2*y(n-1/sym.pi)-5*y(n-2)
    sym.rsolve(f,y(n),[1,4])

.. nboutput:: rst
    :execution-count: 10

    .. math::
        :nowrap:

        $$\left(\sqrt{5} i\right)^{\alpha} \left(\frac{1}{2} - \frac{2 i}{5} \sqrt{5}\right) + \left(- \sqrt{5} i\right)^{\alpha} \left(\frac{1}{2} + \frac{2 i}{5} \sqrt{5}\right)$$

