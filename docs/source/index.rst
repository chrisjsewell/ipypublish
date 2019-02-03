.. image:: _static/logo_name.png
    :alt: **IPyPublish**

A package for creating and editing publication ready scientific reports and presentations,
from Jupyter Notebooks.

.. attention::

    A major API improvement occurred in ``v0.7.0``.
    This has not changed the general user interface,
    but anyone using custom converter plugins will be required to update them
    (see :ref:`convert_from_old_api`)

.. todo:: update gif

.. figure:: https://github.com/chrisjsewell/ipypublish/raw/master/example_workflow.gif
    :alt: example_workflow.gif


IPyPublish: Features
====================

Combining features of the Jupyter Notebook,
WYSIWYG editors and the Latex document preparation system,
to provide a workflow for:

- Dynamic editing and visualisation of key document components
  (text, math, figures, tables, references, citations, etc).

- Combine document elements with dynamic (and reproducible) data exploration,
  analysis and visualisation.

- Supply meta formatting for document and code elements for precise control
  over the final document layout and typesetting.

- Output the same source document to different layouts and formats
  (pdf, html, presentation slides, etc).

.. figure:: _static/process.svg
    :align: center
    :height: 300px
    :alt: conversion process
    :figclass: align-center

Citation
========

Please cite |DOI| if using IPyPublish.


Badges
======

|Build Status| |Coverage Status| |PyPI|

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   examples
   notebook_conversion
   metadata_tags
   custom_export_config
   additional_tools
   applications
   acknowledgements
   package_api
   releases

.. toctree::
   :maxdepth: 2
   :caption: Included Files:

   latex_ipypublish_all
   export_schema
   outline_schema
   segment_example
   metadata_doc_schema


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
