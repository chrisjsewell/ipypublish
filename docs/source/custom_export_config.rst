.. _customise_conversion:

Customising the Conversion Process
==================================

The entire conversion process is controlled by the
:py:class:`ipypublish.convert.main.IpyPubMain` configurable class,
which can be parsed a configuration file, in JSON format.

The simplest customisation, would be to copy
:ref:`latex_ipypublish_all.json <latex_ipypublish_all>`
(or the html/slides variants) and make changes to the
``cell_defaults`` and ``nb_defaults`` dictionaries, to suit your output
needs, then run:

.. code-block:: console

    nbpublish -f path/to/latex_ipypublish_all.json notebook.ipynb

Outline of the Process
----------------------

IPyPublish uses configuration files to control how the Notebook(s) will
be exported. As shown in the figure below, they define three key components:

1. The export class, and its associated pre-processors and filter functions.
2. The `jinja`_ template outline and segments to be inserted into it.
3. The type and order of post-processors.

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
- A new set of :py:class:`ipypublish.postprocessors.base.IPyPostProcessor`
  plugin classes, to handle post-processing of outputs.
- The use of ``latexmk`` with XeLaTeX to convert TeX to PDF,
  and correct resolution of file references and citations.

.. versionadded:: v0.8.3

    Drag and drop cell attachments are now extracted and correctly referenced

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
                "file": "latex_outline.latex.j2"
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
        },
        "postprocessors": {
            "order": [
                "remove-blank-lines",
                "remove-trailing-space",
                "filter-output-files",
                "remove-folder",
                "write-text-file",
                "write-resource-files",
                "copy-resource-paths"
            ]
        }
    }


Exporter Class
~~~~~~~~~~~~~~

On line 6, we define the exporter class, which can be any class in the python
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

On line 22, we define how to construct the `jinja`_ template.
The ``outline`` key defines the path to an outline template,
such as in :ref:`outline_schema`.

.. versionchanged:: 0.8.0

    The outline file is now a jinja template, instead of a JSON file

This template file can be a full jinja template file, extending
an existing nbconvert template, but may optionally contain 'placeholders'
(of the form ``@ipubreplace{below}{key_name}``)
that can be replaced by injecting zero or more segments into them.
The first option states whether segment injections are appended above or below
previous injections, and the second option defines the key for that segment.

This approach allows independent aspects of the document to be stored
separately then pieced together in the desired manner. For example,
the segment file in :ref:`segment_config` defines only parts of the document
which control how the bibliography is constructed.
This could be removed or replaced by a custom export configuration.
Similarly, input and output prompts can be added/removed in html documents.

Segments are applied in the order they are defined, and appended
above or below existing content, as defined by the placeholder.
For example, these segments:

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

applied to this template outline:

.. code-block:: html+jinja

    {% block markdowncell scoped %}
    @ipubreplace{above}{notebook_input_markdown_pre}
    @ipubreplace{below}{notebook_input_markdown}
    @ipubreplace{below}{notebook_input_markdown_post}
    {% endblock markdowncell %}

will result in a template containing:

.. code-block:: html+jinja

    {% block markdowncell scoped %}
    <div class='outer'>
    <div class='inner'>
        test
    </div>
    </div>
    {% endblock markdowncell %}


Segment configuration files also have an optional ``overwrite`` key, which
define segments that overwrite any previously defined content in that section.

.. seealso::

    - The jinja documentation on :doc:`jinja:templates`

    - The nbconvert documentation on :doc:`nbconvert:customizing`

.. _post-processors:

Post-Processors
---------------

On line 38 we define how to post-process the converted output and resources.
See :py:mod:`ipypublish.postprocessors` for a list of built-in post-processors,
which include, outputting to file or stdout, dumping files to a folder,
and running ``latexmk`` or ``sphinx-build``.

Additional post-processors may be registered as named `entry_points`_.
ipypublish uses the ``ipypublish.postprocessors`` entry point to find
post-processors from any package you may have installed.

If you are writing a Python package that provides custom post-processors,
you can register them in your package's :file:`setup.py`. For
example, your package may contain one named "simple",
which would be registered in your package's :file:`setup.py` as follows:

.. code-block:: python

    setup(
        ...
        entry_points = {
            'ipypublish.postprocessors': [
                'simple = mymodule:SimplePostProcessor'
            ],
        }
    )

.. _entry_points: https://packaging.python.org/en/latest/distributing/#entry-points

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
