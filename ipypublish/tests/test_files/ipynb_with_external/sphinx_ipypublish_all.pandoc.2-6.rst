
.. An html document created by ipypublish
   outline: ipypublish.templates.outline_schemas/rst_outline.rst.j2
   with segments:
   - nbsphinx-ipypublish-content: ipypublish sphinx content

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

This is a long section of text, which we only want in a document (not a
presentation) some text some more text some more text some more text
some more text some more text some more text some more text some more
text

References and Citations
------------------------

References to :numref:`fig:example`, :numref:`tbl:example`,
:eq:`eqn:example_sympy` and :numref:`code:example_mpl`.

A latex citation. :cite:`zelenyak_molecular_2016`

A html citation. :cite:`kirkeminde_thermodynamic_2012`

Todo notes
----------

.. todo:: an inline todo

Some text.

.. todo:: a todo in the margins

Text Output
===========

.. nbinput:: ipython3
    :execution-count: 3
    :no-output:

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

        This is some printed text,
        with a nicely formatted output.

Images and Figures
==================

.. nbinput:: ipython3
    :execution-count: 3
    :no-output:

    Image('example.jpg',height=400)

.. nboutput:: rst

    .. figure:: ipynb_with_external_files/output_13_0.jpeg
        :alt: output_13_0
        :align: center
        :height: 400
        :name: fig:example

        A nice picture.

Displaying a plot with its code
-------------------------------

.. nbinput:: ipython3
    :execution-count: 9
    :no-output:
    :name: code:example_mpl
    :caption: The plotting code for a matplotlib figure (:numref:`fig:example_mpl`).

    plt.scatter(np.random.rand(10), np.random.rand(10),
                label='data label')
    plt.ylabel(r'a y label with latex $\alpha$')
    plt.legend();

.. nboutput:: rst

    .. figure:: ipynb_with_external_files/output_17_0.svg
        :alt: output_17_0
        :align: center
        :name: fig:example_mpl

        A matplotlib figure, with the caption set in the markdowncell above the
        figure.

Tables (with pandas)
====================

.. nbinput:: ipython3
    :execution-count: 8
    :no-output:
    :name: code:example_pd
    :caption: The plotting code for a pandas Dataframe table (:numref:`tbl:example`).

    df = pd.DataFrame(np.random.rand(3,4),columns=['a','b','c','d'])
    df.a = ['$\delta$','x','y']
    df.b = ['l','m','n']
    df.set_index(['a','b'])
    df.round(3)

.. nboutput:: rst

    .. table:: An example of a table created with pandas dataframe.
        :name: tbl:example

        == ============== = ===== =====
        \  a              b c     d
        == ============== = ===== =====
        0  :math:`\delta` l 0.583 0.279
        1  x              m 0.914 0.021
        2  y              n 0.333 0.116
        == ============== = ===== =====

Equations (with ipython or sympy)
=================================

.. nbinput:: ipython3
    :execution-count: 9
    :no-output:

    Latex('$$ a = b+c $$')

.. nboutput:: rst

    .. math::
        :nowrap:
        :label: eqn:example_ipy

        \begin{equation}
         a = b+c
        \end{equation}

.. nbinput:: ipython3
    :execution-count: 10
    :no-output:
    :name: code:example_sym
    :caption: The plotting code for a sympy equation (:eq:`eqn:example_sympy`).

    y = sym.Function('y')
    n = sym.symbols(r'\alpha')
    f = y(n)-2*y(n-1/sym.pi)-5*y(n-2)
    sym.rsolve(f,y(n),[1,4])

.. nboutput:: rst

    .. math::
        :nowrap:
        :label: eqn:example_sympy

        \begin{equation}
        \left(\sqrt{5} i\right)^{\alpha} \left(\frac{1}{2} - \frac{2 i}{5} \sqrt{5}\right) + \left(- \sqrt{5} i\right)^{\alpha} \left(\frac{1}{2} + \frac{2 i}{5} \sqrt{5}\right)
        \end{equation}

.. bibliography:: ipynb_with_external_files/example.bib
