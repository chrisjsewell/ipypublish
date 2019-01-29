.. todo:: update a

Custom Export Configurations
============================

The Conversion Process
----------------------

iPyPublish uses export configuration files to control how the Notebook(s)
will be exported. As shown in the figure below, they define two key components:

1. The export class, and its associated pre-processors and filter functions.
2. The Jinja template outline and segments to be inserted into it.

.. figure:: _static/process.svg
    :align: center
    :height: 400px
    :alt: conversion process
    :figclass: align-center

This process extends :py:mod:`nbconvert` in a number of ways:

- Merging of notebooks is handled automatically
- Numerous additional :py:mod:`ipypublish.preprocessors` and
  :py:mod:`ipypublish.filters` are supplied.
- Jinja templates are constructed *via* segment insertions,
  into a skeleton (outline) template, rather than by inheritance only.
  This allows for greater control and flexibility over its construction.
- The use of ``latexmk`` to convert TeX to PDF and correct resolution of
  references and citations.

The Configuration File Format
-----------------------------

The configuration file is a JSON file, with a validation schema
:ref:`export_config_schema` 

.. code:: json

    {
      "description": [
        "A description of the configuration"
      ],
      "exporter": {
        "class": "nbconvert.exporters.LatexExporter",
        "filters": {
          "remove_dollars": "ipypublish.filters.filters.remove_dollars",
        },
        "preprocessors": [
          {
            "class": "ipypublish.preprocessors.split_outputs.SplitOutputs",
            "args": {
              "split": true
            }
          }
        ],
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
            "file": "ipy-contents_framed_code.latex-tpl.json"
          }
        ]
      }
    }



.. todo:: remove all stuff below here

On instantiation, ipypublish loads all converter plugins in its internal
:py:mod:`ipypublish.export_plugins`
module folder. Additionally, when ``nbpublish`` or ``nbpresent`` are called, if
a folder named **ipypublish_plugins** is present in the current working
directory, they will load all plugins in this folder.

The simplest application of this, would be to copy the a

`latex_ipypublish_all.json <https://github.com/chrisjsewell/ipypublish/blob/master/ipypublish/export_plugins/latex_ipypublish_all.json>`__
file (or the html/slides variants) and make changes to the
``cell_defaults`` and ``nb_defaults`` dictionaries to suit your output
needs.

A plugin is a python (.py) file with at least the following four
variables (i.e. it’s interface spec):

1. a **docstring** describing its output format
2. an **oformat** string, specifying a base exporter prefix (for any of
   the exporters listed
   `here <https://nbconvert.readthedocs.io/en/latest/api/exporters.html#specialized-exporter-classes>`__)
3. a **config** dictionary, containing any configuration option (as a
   string) listed
   `here <https://nbconvert.readthedocs.io/en/latest/api/exporters.html#specialized-exporter-classes>`__.
   This is mainly to supply preprocessors (which act on the notbook
   object before it is parsed) or filters (which are functions supplied
   to the jinja template).
4. a **template** string, specifying the `Jinja
   templates <https://jinja2.readthedocs.io/en/latest/intro.html>`__,
   which contains rules for how each element of the notebook should be
   converted, and also what each section of the latex file should
   contain.
5. It is not required, but recommended, to also include the version
   number of ipypublish which the plugin was written for.

So a simple plugin would look like this (create_tplx will be explained
below)

.. code:: python

   """this exporter exports a .tex file with nothing in it
   """
   from ipypublish.latex.create_tplx import create_tplx
   oformat = 'Latex'
   config = {}
   template = create_tplx()

This is similar to how nbconvert works, except for one key difference,
the plugin must specify the entire jinja template (rather than using a
default one). The advantage of this, is that the plugin has complete
control over the look of the final document.

To aid in the creation of the jinja template, the ``create_tplx`` (for
latex) and ``create_tpl`` (for html) functions work by creating an
inital *skeleton* template, with placeholders in all the relevant
`structural
blocks <https://nbconvert.readthedocs.io/en/latest/customizing.html#Template-structure>`__.
They then take a list of *fragment* dictionaries which progressively
append input to the relevant blocks. So, for instance:

.. code:: python

   """exports a .tex file containing 
   some latex setup and
   only input markdown cells from the notebook 
   """
   from ipypublish.latex.create_tplx import create_tplx
   oformat = 'Latex'
   config = {}

   doc_dict = {
       'document_docclass':r'\documentclass[11pt]{article}',
       'document_packages':r"""
       \usepackage{caption}
        \usepackage{amsmath}
       """
   }

   mkdown_dict = {
     'notebook_input_markdown':r"""
       ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex') )))
       """
   }

   template = create_tplx([doc_dict,mkdown_dict])

This approach allows independant aspects of the document to be stored
separately then pieced together in the desired manner. ipypublish stores
all of the standard fragments in separate modules, for instance the
latex_standard_article plugin looks like this:

.. code:: python

   """latex article in the standard nbconvert format
   """

   from ipypublish.latex.create_tplx import create_tplx
   from ipypublish.latex.standard import standard_article as doc
   from ipypublish.latex.standard import standard_packages as package
   from ipypublish.latex.standard import standard_definitions as defs
   from ipypublish.latex.standard import standard_contents as content
   from ipypublish.latex.standard import in_out_prompts as prompts

   oformat = 'Latex'
   template = create_tplx(
       [package.tplx_dict,defs.tplx_dict,doc.tplx_dict,
       content.tplx_dict,prompts.tplx_dict])

   config = {}

Now, if you wanted mainly the same output format but without input and
output prompts shown, simply copy this plugin but remove the
prompts.tplx_dict.

By default, sections are appended to, so;

.. code:: python

   dict1 = {'notebook_input':'a'}
   dict2 = {'notebook_input':'b'}
   template = create_tplx([dict1,dict2])

would show a, then b. But, if you want to redefine a particular
section(s);

.. code:: python

   dict1 = {'notebook_input':'a'}
   dict2 = {
       'overwrite':['notebook_input'],
       'notebook_input':'b'}
   template = create_tplx([dict1,dict2])

will only show b.

Note that, the ``create_tpl`` template additionally has *pre* and *post*
placeholder. This is helpful for wrapping cells in extra html tags. For
instance:

.. code:: python


   dict1 = {
     'notebook_input_markdown_pre':r"<div class="inner">",
     'notebook_input_markdown':"test",
     'notebook_input_markdown_post':r"</div>",
   }
   dict2 = {
     'notebook_input_markdown_pre':r"<div class="outer">",
     'notebook_input_markdown_post':r"</div>",
   }

   template = create_tpl([dict1,dict2])

will result in a template containing:

.. code:: html

   <div class="outer">
   <div class="inner">
   test
   </div>
   </div>