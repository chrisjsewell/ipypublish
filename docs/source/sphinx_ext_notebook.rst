.. _sphinx_ext_notebook:

ipypublish.sphinx.notebook
==========================

:py:mod:`ipypublish.sphinx.notebook` is adapted from
`nbsphinx <https://nbsphinx.readthedocs.io>`_, to provide a
`sphinx extension <https://www.sphinx-doc.org/en/master/usage/extensions/>`_
for converting notebooks with :py:class:`ipypublish.convert.main.IpyPubMain`.

This website is built using it,
so a good example of its use would be to look at the
`ipypublish/docs/source/conf.py <https://github.com/chrisjsewell/ipypublish/blob/master/docs/source/conf.py>`_.

This extension loads:

- ``nbinput``, ``nboutput``, ``nbinfo`` and ``nbwarning`` directives,
  that *wrap* input and output notebook cells
  (see :py:mod:`ipypublish.sphinx.notebook.directives`)
- a source parser for files with the ``.ipynb`` extension
  (see :py:class:`ipypublish.sphinx.notebook.parser.NBParser`)

Usage
-----

The key addition to the sphinx configuration file (conf.py) is:

.. code-block:: python

    extensions = [
        'ipypublish.sphinx.notebook'
    ]

Each notebook will be converted according to an ipypublish configuration file,
specified by the option ``ipysphinx_export_config``.
The two recommended configurations to use are either:

- ``sphinx_ipypublish_all.ext``
  will execute all cells in the notebook before converting to an .rst file.
- ``sphinx_ipypublish_all.ext.noexec``
  will convert the notebook to an .rst file with no initial execution
  (i.e. the notebook should be saved with outputs).

The extension is also pre-configured to convert .Rmd files,
using `jupytext <https://github.com/mwouts/jupytext>`_ (see :ref:`markdown_cells`).
To turn this feature on (for sphinx>=1.8):

.. code-block:: python

    source_suffix = {
        '.rst': 'restructuredtext',
        '.ipynb': 'jupyter_notebook',
        '.Rmd': 'jupyter_notebook'
    }

or for sphinx<1.8:

.. code-block:: python

    source_parsers = {
        '.Rmd': 'ipypublish.sphinx.notebook.parser.NBParser'
    }

.. important::

    To use the sphinx extension,
    IPyPublish must be installed with the sphinx extras:

    ``pip install ipypublish[sphinx]``

    or the conda install already contains these extras.

.. tip::

    To convert a notebook directly to HTML *via* sphinx,
    you can run:

    ``nbpublish -f sphinx_ipypublish_main.run notebook.ipynb``

    This will convert the notebook to .rst, create a basic conf.py file
    (including the ipypublish extensions), and
    call `sphinx-build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html>`_.

.. seealso::

    :ref:`sphinx_doc_metadata`, for the notebook document level metadata options.

Configuration
-------------

Additional configuration can be added,
as described in :numref:`tbl:sphinx_config`, and numbered figures etc can be
setup by adding to the conf.py:

.. code-block:: python

    numfig = True
    math_numfig = True
    numfig_secnum_depth = 2
    numfig_format: {'section': 'Section %s',
                    'figure': 'Fig. %s',
                    'table': 'Table %s',
                    'code-block': 'Code Block %s'}
    math_number_all = True

    mathjax_config = {
        'TeX': {'equationNumbers': {'autoNumber': 'AMS', 'useLabelIds': True}},
    }

.. important::

    To number items, the initial toctree must include the ``:numbered:`` option

.. table:: Configuration values to use in conf.py
    :name: tbl:sphinx_config

    ============================= =========================== =======================================================================
    Name                          Default                     Description
    ============================= =========================== =======================================================================
    ipysphinx_export_config       "sphinx_ipypublish_all.ext" ipypublish configuration file to use for conversion to .rst
    ipysphinx_folder_suffix       "_nbfiles"                  <fname><suffix> for dumping internal images, etc
    ipysphinx_overwrite_existing  False                       raise error if nb_name.rst already exists
    ipysphinx_config_folders      ()                          additional folders containing ipypublish configuration files
    ipysphinx_show_prompts        False                       show cell prompts
    ipysphinx_input_prompt        "[{count}]:"                format of input prompts
    ipysphinx_output_prompt       "[{count}]:"                format of output prompts
    ipysphinx_input_toggle        False                       add a button at the right side of input cells, to toggle show/hide
    ipysphinx_output_toggle       False                       add a button at the right side of output cells, to toggle show/hide
    ipysphinx_preconverters       {}                          a mapping of additional file extensions to pre-conversion functions
    ipysphinx_require_jsurl       cdnjs.cloudflare.com<2.3.4> source URL for require package javascript
    ipysphinx_requirejs_option    {}                          additional options for require package javascript ``<script>`` tag
    ipysphinx_widgets_jsurl       <obtained from package>     source URL for ipywidgets embedding javascript
    ipysphinx_widgetsjs_options   {}                          additional options for require package javascript ``<script>`` tag
    ipysphinx_always_add_jsurls   False                       Add javascript URLs to all pages (or only those created from notebooks)
    ============================= =========================== =======================================================================

Examples
--------

Basic input
~~~~~~~~~~~

.. code-block:: rst

    .. nbinput:: python
       :execution-count: 2
       :caption: A caption for the code cell
       :name: ref_label

       print("hallo")

.. nbinput:: python
    :execution-count: 2
    :caption: A caption for the code cell
    :name: ref_label
    :no-output:

    print("hallo")


Basic output
~~~~~~~~~~~~

.. code-block:: rst

    .. nboutput::
       :execution-count: 2

       hallo

.. nboutput::
    :execution-count: 2

    hallo

.. _sphinx_ext_notebook_toggle_in:

Toggle inputs/outputs
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

    .. nbinput-toggle-all:: NbInput Toggle All

    .. nboutput-toggle-all:: NbOutput Toggle All

    .. nbinput:: python
        :add-toggle:
        :execution-count: 3

        j = 0
        for i in range(3):
            print(i)
            j += i
        print(j)

    .. nboutput::
        :add-toggle:
        :execution-count: 3

        hallo
        there

.. nbinput-toggle-all:: NbInput Toggle All

.. nboutput-toggle-all:: NbOutput Toggle All

.. nbinput:: python
    :add-toggle:
    :execution-count: 3

    j = 0
    for i in range(3):
        print(i)
        j += i
    print(j)

.. nboutput::
    :add-toggle:
    :execution-count: 3

    hallo
    there

Information and Warnings
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

    .. nbinfo:: Some information

.. nbinfo:: Some information

.. code-block:: rst

    .. nbwarning:: This is a warning

.. nbwarning:: This is a warning
