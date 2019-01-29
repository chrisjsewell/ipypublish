Custom Export Configurations
============================

The simplest application of this, would be to copy
:ref:`latex_ipypublish_all.json <latex_ipypublish_all>`
(or the html/slides variants) and make changes to the
``cell_defaults`` and ``nb_defaults`` dictionaries, to suit your output
needs, then run:

.. code-block:: console

    nbpublish -f path/to/latex_ipypublish_all.json notebook.ipynb

The Conversion Process
----------------------

iPyPublish uses export configuration files to control how the Notebook(s)
will be exported. As shown in the figure below, they define two key components:

1. The export class, and its associated pre-processors and filter functions.
2. The `jinja`_ template outline and segments to be inserted into it.

.. figure:: _static/process.svg
    :align: center
    :height: 400px
    :alt: conversion process
    :figclass: align-center

    iPyPublish Conversion Process

This process extends :py:mod:`nbconvert` in a number of ways:

- Merging of notebooks is handled automatically
- Numerous additional :py:mod:`ipypublish.preprocessors` and
  :py:mod:`ipypublish.filters` are supplied.
- `jinja`_ templates are constructed *via* segment insertions,
  into a skeleton (outline) template, rather than by inheritance only.
  This allows for greater control and modularity in their construction.
- The use of ``latexmk`` with XeLaTeX to convert TeX to PDF,
  and correct resolution of file references and citations.


The Configuration File Format
-----------------------------

The configuration file is a JSON file, with a validation schema given in
:ref:`export_config_schema`. Below is a minimal example:

.. code-block:: json
    :linenos:

    {
        "description": [
        "A description of the configuration"
        ],
        "exporter": {
            "class": "nbconvert.exporters.LatexExporter",
            "preprocessors": [
                {
                "class": "ipypublish.preprocessors.latex_doc_links.LatexDocLinks",
                "args":
                    {
                    "metapath": "${meta_path}",
                    "filesfolder": "${files_path}"
                    }
                }
            ],
            "filters": {
                "remove_dollars": "ipypublish.filters.filters.remove_dollars",
            },
            "other_args": {}
        },
        "template": {
            "outline": {
                "module": "ipypublish.templates.outline_schemas",
                "file": "latex_tplx_schema.json"
            },
            "segments": [
                {
                "module": "ipypublish.templates.segments",
                "file": "std-standard_packages.latex-tpl.json"
                },
                {
                "directory": "path/to/folder",
                "file": "a_user_defined_segment.json"
                }
            ]
        }
    }


Exporter Class
~~~~~~~~~~~~~~

In line 6, we define the exporter class, which can be any class in the python
environment namespace that inherits from
:py:class:`nbconvert.exporters.Exporter`.

Exporters can be parsed any number of preprocessors
(inheriting from :py:class:`nbconvert.preprocessors.Preprocessor`),
which act on the notebook in the order supplied.

The ``args`` field is used to set any configurable :py:mod:`traitlets`
the class exposes.
Two special placeholders are available:

- ``${meta_path}`` will be set dynamically as the path to the (primary)
  ipynb file, containing the document level meta-data.
- ``${files_path}`` will be set dynamically as the path to the folder where,
  additional files (such as internal images) will be output to.

Filters provide functions or classes to transform particular content of the
notebook, and are parsed to the `jinja`_ templating engine.

.. seealso::

    - The classes available natively in nbconvert:
      :py:mod:`nbconvert.exporters`,
      :py:mod:`nbconvert.preprocessors`,
      :py:mod:`nbconvert.filters`.

    - How :ref:`jinja:filters` are used in `jinja`_.

Template Construction
~~~~~~~~~~~~~~~~~~~~~

In line 22, we define how to construct the `jinja`_ template.
The ``outline`` key defines the path to an outline schema,
such as in :ref:`outline_schema`.
This file achieves two things; to define an outline of the `jinja`_ template
structural blocks,
with placeholders to be replaced by :py:func:`str.format`, and to
provide a schema for segment files which are used to replace
one or more of the placeholders.

This approach allows independent aspects of the document to be stored
separately then pieced together in the desired manner. For example,
the segment defined in :ref:`segment_config` defines only parts of the document
which define how the bibliography is constructed.
This could be removed or replaced by a custom export configuration.
Similarly, input and output prompts can be added/removed in html documents.

Segments are applied in the order they are defined,
and the outline schema defines whether they are appended
above or below existing content. For example, these segments:

.. code-block:: JSON

    [
        {
            "notebook_input_markdown_pre": "<div class='inner'>",
            "notebook_input_markdown": "  test",
            "notebook_input_markdown_post": "</div>",
        },
        {
            "notebook_input_markdown_pre": "<div class='outer'>",
            "notebook_input_markdown_post": "</div>",
        }
    ]

will result in a template containing:

.. code-block:: html

   <div class='outer'>
   <div class='inner'>
     test
   </div>
   </div>


Segment configuration files also have an optional ``overwrite`` key, which
define segments that overwrite any previously defined content in that section.

.. seealso::

    - The jinja documentation on :doc:`jinja:templates`

    - The nbconvert documentation on :doc:`nbconvert:customizing`

Loading Custom Configurations
-----------------------------

Custom configurations can be parsed directly to ``nbpublish``:

.. code-block:: console

    nbpublish -f path/to/configs/export_config.json notebook.ipynb

Or used as a key, by providing ``nbpublish`` with additional folders to scan
(in addition to the :py:mod:`ipypublish.export_plugins` module folder):

.. code-block:: console

    nbpublish -ep path/to/configs -f export_config notebook.ipynb


.. _convert_from_old_api:

Conversion of Plugins From Old API
----------------------------------

The old style export plugins (defined as python scripts)
can be converted to the new JSON style, using the
:py:func:`ipypublish.port_api.plugin_to_json.convert_to_json` function.

The old style template segment dictionaries (defined as python scripts)
can be converted to the new JSON style, using the
:py:func:`ipypublish.port_api.tpl_dct_to_json.py_to_json` function.


.. links:

.. _jinja: http://jinja.pocoo.org/
.. _filter: http://jinja.pocoo.org/docs/dev/templates/#filters
.. _reveal.js: http://lab.hakim.se/reveal-js
.. _pandoc: http://pandoc.org/
