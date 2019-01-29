.. _notebook_conversion:

Notebook Conversion
===================

Setting up a Notebook
---------------------

For improved latex/pdf output, ``ipynb_latex_setup.py`` contains import
and setup code for the notebook and a number of common packages and
functions, including:

-  numpy, matplotlib, pandas, sympy, …
-  ``images_hconcat``, ``images_vconcat`` and ``images_gridconcat``
   functions, which use the PIL/Pillow package to create a single image
   from multiple images (with specified arrangement)

To use this script, in the first cell of a notebook, insert:

.. code:: python

   from ipypublish.scripts.ipynb_latex_setup import *

It is recommended that you also set this cell as an initialisation cell
(i.e. have ``"init_cell": true`` in the metadata)

For existing notebooks: the **nb_ipypublish_all** and
**nb_ipypublish_nocode** converters (see below) can be helpful for
outputting a notebook, with identical content to that input, but with
default metatags defining how content is to be output.

Converting Notebooks
--------------------

The ``nbpublish`` script handles parsing the notebooks to nbconvert, with
the appropriate converter. To see all options for this script:

.. code-block:: console

   nbpublish -h

For example, to convert the Example.ipynb notebook directly to pdf:

.. code-block:: console

   nbpublish -pdf example/notebooks/Example.ipynb

If a folder is input, then the .ipynb files it contains are processed
and combined in ‘natural’ sorted order, i.e. 2_name.ipynb before
10_name.ipynb. By default, notebooks beginning ’_’ are ignored.

All available converters are also listed by ``nbpublish --list-exporters``.
Three of note are:

-  **latex_ipypublish_main** is the **default** and converts cells to
   latex according to metadata tags on an ‘opt in’ basis. Note that, for
   this converter, **no code cells or output** will appear in the final
   tex/pdf document unless they have a suitable `ipub metadata
   tag <#latex-metadata-tags>`__.
-  **html_ipypublish_main** converts the entire notebook(s) to html and
   adds a table of contents sidebar and a button to toggle input code
   and output cells visible/hidden, with latex citations and references
   resolved.
-  **slides_ipypublish_main** converts the notebook to
   `reveal.js <http://lab.hakim.se/reveal-js/#/>`__ slides, with latex
   citations and references resolved and slide partitioning by markdown
   headers. See the `Live Slideshows <#live-slideshows>`__ section for
   using ``nbpresent`` to serve these slides to a webbrowser.
-  The **all** and **nocode** variants of these converters preprocess a
   copy of the notebook, to add default metadata tags to the notebook
   and all cells, such that all output is rendered (with or without the
   code)

The current ``nbconvert --to pdf`` does not correctly resolve references
and citations (since it copies the files to a temporary directory).
Therefore nbconvert is only used for the initial
``nbconvert --to latex`` phase, followed by using ``latexmk`` to create
the pdf and correctly resolve everything. **To convert your own notebook
to PDF** for the first time, a good route would be to use:

.. code-block:: console

   nbpublish -f latex_ipypublish_all -pdf --pdf-debug path/to/YourNotebook.ipynb

.. note::

   To raise any issues, please include the
   `converted/YourNotebook.nbpub.log file`.

The IPyPublish Defaults
-----------------------

The ipypublish ‘main’ converters are designed with the goal of creating
a single notebook, which may contain lots of exploratory code/outputs,
mixed with final output, and that can be output as both a document
(latex/pdf or html) and a presentation (reveal.js). The logic behind the
default output is then:

-  For documents: all headings and body text is generally required, but
   only a certain subset of code/output
-  For slides: all headings are required, but most of the body text will
   be left out and sustituted with ‘abbreviated’ versions, and only a
   certain subset of code/output.

This leads to the following logic flow (discussed further in the
`Metadata Tags <#metadata-tags>`__ section):

**latex_ipypublish_main**/**html_ipypublish_main**:

-  all cells: bypass “ignore” and “slideonly” tags
-  markdown cells: include all
-  code cells (input): only include if the “code” tag is present
-  code cells (output): only include if the following tags are present

   -  “figure” for png/svg/pdf/jpeg or html (html only)
   -  “table” or “equation” for latex or html (html only)
   -  “mkdown” for markdown text
   -  “text” for plain text

**slides_ipypublish_main**:

-  all cells: bypass “ignore”
-  markdown cells: are first split into header (beggining #)/non-header
   components

   -  headers: include all
   -  non-headers: only include if “slide” tag

-  code cells (input): only include if the “code” tag is present
-  code cells (output): only include if the following tags are present

   -  “figure” for png/svg/pdf/jpeg/html
   -  “table” or “equation” for latex/html
   -  “mkdown” for markdown text
   -  “text” for plain text

Packages, such as pandas and matplotlib, use jupyter notebooks `rich
representation <http://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display>`__
mechanics to store a single output in multiple formats. nbconvert (and
hence ipypublish) then selects only the highest priority (compatible)
format to be output. This allows, for example, for pandas DataFrames to
be output as latex tables in latex documents and html tables in html
documents/slides.

