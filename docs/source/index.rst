.. image:: _static/logo_name.png
    :alt: **IPyPublish**

A package for creating and editing publication ready scientific reports
and presentations, from Jupyter Notebooks.


.. figure:: _static/main_image.*
    :width: 60%
    :align: center
    :alt: image of cycle


.. attention::

    IPyPublish is evolving!
    Please see :ref:`releases` for all the exciting new feature.

    Also see `pytest-notebook <https://pytest-notebook.readthedocs.io>`_,
    for a new tool to test and regenerate notebooks.


IPyPublish: Features
====================

Combining features of the Jupyter Notebook,
WYSIWYG editors, Latex document preparation system and Sphinx HTML creation,
to provide a workflow for:

- Dynamic editing and visualisation of key document components
  (text, math, figures, tables, references, citations, etc).

- Combine document elements with dynamic (and reproducible) data exploration,
  analysis and visualisation.

- Supply meta formatting for document and code elements for precise control
  over the final document layout and typesetting.

- Output the same source document to different layouts and formats
  (pdf, html, presentation slides, etc).

Another strength of IPyPublish,
is that it is almost entirely modular and configurable, making it very easy to
modify or extend the current functionality.


Citation
========

Please cite |DOI| if using IPyPublish.


Badges
======

|Build Status| |Coverage Status| |PyPI| |Conda|

.. toctree::
   :maxdepth: 1
   :numbered:
   :caption: Using IPyPublish
   :hidden:

   getting_started
   code_cells
   markdown_cells
   nb_conversion
   metadata_tags
   custom_export_config

.. toctree::
   :maxdepth: 1
   :caption: Sphinx Extensions
   :hidden:

   sphinx_extensions
   sphinx_ext_notebook
   sphinx_ext_bibgloss

.. toctree::
   :maxdepth: 1
   :caption: Additional Information
   :hidden:

   releases
   examples
   applications
   dev_guide
   additional_tools
   acknowledgements
   package_api

.. toctree::
   :maxdepth: 1
   :caption: Validation Schemas
   :hidden:

   metadata_doc_schema
   metadata_cell_schema
   export_schema


.. todo:: how to use with vs-code

Index and Search
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |Build Status| image:: https://travis-ci.org/chrisjsewell/ipypublish.svg?branch=master
   :target: https://travis-ci.org/chrisjsewell/ipypublish
.. |Coverage Status| image:: https://coveralls.io/repos/github/chrisjsewell/ipypublish/badge.svg?branch=master
   :target: https://coveralls.io/github/chrisjsewell/ipypublish?branch=master
.. |PyPI| image:: https://img.shields.io/pypi/v/ipypublish.svg
   :target: https://pypi.python.org/pypi/ipypublish/
.. |DOI| image:: https://zenodo.org/badge/96322423.svg
   :target: https://zenodo.org/badge/latestdoi/96322423
.. |Conda| image:: https://anaconda.org/conda-forge/ipypublish/badges/version.svg
   :target: https://anaconda.org/conda-forge/ipypublish
