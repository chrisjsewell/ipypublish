
.. An html document created by ipypublish
   outline: ipypublish.templates.outline_schemas/rst_outline.rst.j2
   with segments:
   - sphinx-standard-content: standard sphinx nbconvert content

.. code:: ipython3

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

This is an abbreviated section of the document text, which we only want
in a presentation

-  summary of document text

References and Citations
------------------------

References to :raw-latex:`\cref{fig:example}`,
:raw-latex:`\cref{tbl:example}`, :raw-latex:`\cref{eqn:example_sympy}`
and :raw-latex:`\cref{code:example_mpl}`.

A latex citation.:raw-latex:`\cite{zelenyak_molecular_2016}`

A html citation.(Kirkeminde, 2012)

Todo notes
----------

.. raw:: latex

   \todo[inline]{an inline todo}

Some text.:raw-latex:`\todo{a todo in the margins}`

Text Output
===========

.. code:: ipython3

    print("""
    This is some printed text,
    with a nicely formatted output.
    """)

.. parsed-literal::

    This is some printed text,
    with a nicely formatted output.

Images and Figures
==================

.. code:: ipython3

    Image('example.jpg',height=400)

.. image:: ipynb_with_external_files/output_13_0.jpeg
   :height: 400px

Displaying a plot with its code
-------------------------------

A matplotlib figure, with the caption set in the markdowncell above the
figure.

The plotting code for a matplotlib figure
(:raw-latex:`\cref{fig:example_mpl}`).

.. code:: ipython3

    plt.scatter(np.random.rand(10), np.random.rand(10), 
                label='data label')
    plt.ylabel(r'a y label with latex $\alpha$')
    plt.legend();

Tables (with pandas)
====================

The plotting code for a pandas Dataframe table
(:raw-latex:`\cref{tbl:example}`).

.. code:: ipython3

    df = pd.DataFrame(np.random.rand(3,4),columns=['a','b','c','d'])
    df.a = ['$\delta$','x','y']
    df.b = ['l','m','n']
    df.set_index(['a','b'])
    df.round(3)

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

Equations (with ipython or sympy)
=================================

.. code:: ipython3

    Latex('$$ a = b+c $$')

.. math::

     a = b+c 

The plotting code for a sympy equation
(:raw-latex:`\cref{eqn:example_sympy}`).

.. code:: ipython3

    y = sym.Function('y')
    n = sym.symbols(r'\alpha')
    f = y(n)-2*y(n-1/sym.pi)-5*y(n-2)
    sym.rsolve(f,y(n),[1,4])

.. math::

    \left(\sqrt{5} i\right)^{\alpha} \left(\frac{1}{2} - \frac{2 i}{5} \sqrt{5}\right) + \left(- \sqrt{5} i\right)^{\alpha} \left(\frac{1}{2} + \frac{2 i}{5} \sqrt{5}\right)

