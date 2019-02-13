
.. An html document created by ipypublish
   outline: ipypublish.templates.outline_schemas/rst_outline.rst.j2
   with segments:
   - nbsphinx-ipypublish-content: ipypublish sphinx content

Notebook to Test Markdown Cells
===============================

Cell with Attached Image
------------------------

.. figure:: nb_markdown_cells_files/attach_1_output_13_0.jpeg
   :alt: output_13_0.jpeg
   :name: fig:id1

   output_13_0.jpeg

:numref:`fig:id1` :numref:`fig:id1`

Cell with Linked Image
----------------------

.. figure:: nb_markdown_cells_files/logo_example.png
   :alt: this is a **caption**
   :name: fig:id2
   :width: 50.0%

   this is a **caption**

Cell with Link to Header
------------------------

:numref:`cell-with-link-to-header`

Cell with Math
--------------

inline: :math:`a = b`

.. math::
   :nowrap:
   :label: eq:id1

   \begin{equation}a = b\end{equation}

.. math::
   :nowrap:
   :label: eq:id2

   \begin{align*}c &= d \\ other &= e\end{align*}

Cell with Table
---------------

.. _`tbl:id`:

.. table:: Caption.

   +-------+-------+---------+
   | A     | B     | A and B |
   +=======+=======+=========+
   | False | False | False   |
   +-------+-------+---------+
   | True  | False | False   |
   +-------+-------+---------+
   | False | True  | False   |
   +-------+-------+---------+
   | True  | True  | True    |
   +-------+-------+---------+

:numref:`tbl:id`

References Using @ Notation
---------------------------

:numref:`cell-with-link-to-header`, and multiple references
:numref:`tbl:id` and :numref:`eq:id1`
