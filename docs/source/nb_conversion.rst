.. _notebook_conversion:

Notebook Conversion
===================

Command Line Interface
----------------------

The ``nbpublish`` script is a command line interface for initialising
and parsing options to the conversion process.
To see all options for this script:

.. code-block:: console

   nbpublish -h

For example, to convert the Example.ipynb notebook directly to PDF:

.. code-block:: console

   nbpublish -pdf -lb example/notebooks/Example.ipynb

If a folder is input, then the .ipynb files it contains are processed
and combined in ‘natural’ sorted order, i.e. 2_name.ipynb before
10_name.ipynb. By default, notebooks beginning ’_’ are ignored.

Python API
----------

``nbpublish`` parses command line inputs to the
:py:class:`ipypublish.convert.main.IpyPubMain` class,
which is a :py:mod:`traitlets.config` Configuration object that controls
the entire conversion process. For example, to list all configurable options:

.. code-block:: python

    from ipypublish.convert.main import IpyPubMain
    IpyPubMain.class_print_help()

.. seealso::

    :ref:`customise_conversion`

Built-in Export Configurations
------------------------------

All available converters are listed by ``nbpublish --list-exporters``.
Some of note are:

.. glossary::

    latex_ipypublish_main
        the **default** and converts cells to latex according to metadata tags
        on an ‘opt in’ basis. Note that, for this converter,
        **no code cells or output** will appear in the final
        tex/pdf document unless they have a suitable `ipub metadata
        tag <#latex-metadata-tags>`__.

    sphinx_ipypublish_main
        converts the entire notebook(s) to an RST file in the
        `Sphinx document generation <http://www.sphinx-doc.org/en/master/>`_,
        format.

    sphinx_ipypublish_main.run
        The same as sphinx_ipypublish_main, but also creates a conf.py
        file and runs `sphinx-build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html>`_,
        to create HTML documentation (see :ref:`sphinx_extensions`).

    html_ipypublish_main
        converts the entire notebook(s) to HTML and adds a table of contents
        sidebar and a button to toggle input code and output cells
        visible/hidden, with latex citations and references resolved.

    slides_ipypublish_main
        converts the notebook to
        `reveal.js <http://lab.hakim.se/reveal-js/#/>`__ slides, with latex
        citations and references resolved and slide partitioning by markdown
        headers. See the `Live Slideshows <#live-slideshows>`__ section for
        using ``nbpresent`` to serve these slides to a web-browser.

The **all** and **nocode** variants of these converters pre-process a
copy of the notebook, to add default metadata tags to the notebook
and all cells, such that all output is rendered (with or without the code)

Variants ending **.exec** will additionally execute the entire notebook
(running all the cells and storing the output), before converting them.

.. important::

    To use sphinx converters,
    IPyPublish must be installed with the sphinx extras:

    ``pip install ipypublish[sphinx]``

    These are already included in the conda install.

A Note on PDF Conversion
~~~~~~~~~~~~~~~~~~~~~~~~

The current ``nbconvert --to pdf`` does not correctly resolve references
and citations (since it copies the files to a temporary directory).
Therefore nbconvert is only used for the initial
``nbconvert --to latex`` phase, followed by using ``latexmk`` to create
the pdf and correctly resolve everything. **To convert your own notebook
to PDF** for the first time, a good route would be to use:

.. code-block:: console

   nbpublish -f latex_ipypublish_all -pdf -pbug -lb path/to/YourNotebook.ipynb


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

latex_ipypublish_main and html_ipypublish_main
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  all cells: bypass “ignore” and “slideonly” tags
-  markdown cells: include all
-  code cells (input): only include if the “code” tag is present
-  code cells (output): only include if the following tags are present

   -  “figure” for png/svg/pdf/jpeg or html (html only)
   -  “table” or “equation” for latex or html (html only)
   -  “mkdown” for markdown text
   -  “text” for plain text

slides_ipypublish_main
~~~~~~~~~~~~~~~~~~~~~~

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

Simple Customisation of Outputs
-------------------------------

To customise the output of the above defaults, simply download one of:

- :download:`latex_ipypublish_all.json
  <../../ipypublish/export_plugins/latex_ipypublish_all.json>`.
- :download:`sphinx_ipypublish_all.json
  <../../ipypublish/export_plugins/html_ipypublish_all.json>`.
- :download:`html_ipypublish_all.json
  <../../ipypublish/export_plugins/html_ipypublish_all.json>`.
- :download:`slides_ipypublish_all.json
  <../../ipypublish/export_plugins/slides_ipypublish_all.json>`.

Then alter the ``cell_defaults`` and ``nb_defaults`` sections, and run:

.. code-block:: console

    nbpublish -f path/to/new_config.json input.ipynb
