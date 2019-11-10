.. _releases:

Releases
========

.. attention::

   A major API improvement occurred in ``v0.7.0``.
   This has not changed the general user interface,
   but anyone using custom converter plugins will be required to update them
   (see :ref:`convert_from_old_api`)

Version 0.10
------------

v0.10.10
~~~~~~~~

Add compatibility of sphinx conversion with
`ipywidgets <https://ipywidgets.readthedocs.io/en/stable/>`_.
For examples see the section in :ref:`code_cells`, and for sphinx extension
configuration see :ref:`sphinx_ext_notebook`.
Note, the sphinx version dependency is now ``>=1.8``.

Additionally the code base has been formatted by
`black <https://github.com/ambv/black>`__,
and some minor bugs/warnings have been fixed.

v0.10.9
~~~~~~~

Improve ipubpandoc filter conversion of equations:

- Ensure equations that are already wrapped in a math environment
  are not wrapped twice.
- For RST output, ensure multi-line equations are correctly indented

v0.10.6 & v0.10.7
~~~~~~~~~~~~~~~~~

Added sphinx option for toggling notebook input and output cells.
For examples see :ref:`sphinx_ext_notebook_toggle_in` and :ref:`code_cells`.

v0.10.5
~~~~~~~

Remove requirement for sphinx < 2.0

v0.10.4
~~~~~~~

Fix image reference clashes in rst files (see chrisjsewell/ipypublish#90)

v0.10.3
~~~~~~~

Minor Improvements to `ipypublish.sphinx.notebook`:

- remove ``sphinx.ext.imgconverter`` from sphinx auto-builds
- add additional known sphinx roles

v0.10.2
~~~~~~~

Update dependency requirements:

- Only require backport dependencies
  for python version older than their implementation
- use ``ordered-set``, instead of ``oset`` dependency,
  since it is better maintained

v0.10.1
~~~~~~~

Minor Improvements to `ipypublish.sphinx.notebook`:

- Formatting of the execution_count is now inserted by:
  ``ipysphinx_input_prompt.format(count=execution_count)``
- Use "Code Cell Output" as placeholder for output image caption

v0.10.0
~~~~~~~

- Added Sphinx extension for glossary referencing: ``ipypublish.sphinx.gls``.
  See :ref:`sphinx_ext_gls`

- Added ``ConvertBibGloss`` post-processor,
  to convert a bibglossary to the required format

- Added notebook-level metadata options for ``bibglossary`` and ``sphinx``
  (see :ref:`meta_doclevel_schema`)

- Large refactoring and improvements for test suite, particularly for testing
  of Sphinx extensions (using the Sphinx pytest fixtures) and creation of the
  ``IpyTestApp`` fixture

- fixed `tornado version restriction <https://github.com/chrisjsewell/ipypublish/issues/71>`_

Back-compatibility breaking changes:

- renamed Sphinx notebook extension from
  ``ipypublish.ipysphinx`` to ``ipypublish.sphinx.notebook``
  (see :ref:`sphinx_ext_notebook`)

- :py:meth:`ipypublish.postprocessors.base.IPyPostProcessor.run_postprocess`
  input signature changed
  (and consequently it has changes for all post-processors)

v0.9

.. code-block:: python

   def run_postprocess(self, stream, filepath, resources):
      output_folder = filepath.parent

v0.10

.. code-block:: python

   def run_postprocess(self, stream, mimetype, filepath, resources):
      output_folder = filepath.parent

Version 0.9
-----------

v0.9.4
~~~~~~

Bug fix for widefigures
(see `issue <https://github.com/chrisjsewell/ipypublish/issues/68>`_),
thanks to @katie-jones

v0.9.3
~~~~~~

Added Conda distribution:

```console
$ conda install -c conda-forge ipypublish
```

v0.9.1 & 0.9.2
~~~~~~~~~~~~~~

Minor big fix to fix blank line between directives and options in RST

v0.9.0
~~~~~~

**Major Improvements**

- Added ``ipubpandoc`` (see :ref:`markdown_cells`)
- Refactored conversion process to
  :py:class:`ipypublish.convert.main.IpyPubMain` configurable class
- Added postprocessors (see :ref:`post-processors`)
- Added Sphinx notebook extension (see :ref:`sphinx_extensions`)
- Added Binder examples to documentation (see :ref:`code_cells`)

Version 0.8
-----------

v0.8.3
~~~~~~

**Handle Cell Attachments**

Images can also be embedded in the notebook itself. Just drag an image
file into the Markdown cell you are just editing or copy and paste some
image data from an image editor/viewer.

The generated Markdown code will look just like a “normal” image link,
except that it will have an attachment: prefix:

::

   ![a stick figure](attachment:stickfigure.png)

In the Jupyter Notebook, there is a special “Attachments” cell tool-bar
which you can use to see all attachments of a cell and delete them, if
needed.


v0.8.1
~~~~~~

**RST Converter**

-  added standard rst/sphinx converter
-  added nbsphinx converter
-  added optional printing of traceback
-  allow segments to be yaml (with yaml.safe_load)
-  added document level metadata schema

v0.8.0
~~~~~~

Outline templates now use a jinja file, instead of json:

-  extracted templates into separate files
-  use template outline file instead of json schema
-  improve front end logging
-  update documentation
-  version bump
-  added tests

Version 0.7
-----------

v0.7.1
~~~~~~

Improved the `dict_to_kwds` filter and added `biboptions` metadata tags.
See :ref:`metadata_tags`

v0.7.0
~~~~~~

**Major API Update**

-  Converted export configurations and templates from python to JSON
-  Added validation schema for configurations and templates
-  added option to control style of bibliography in latex
-  Converted script executables to console entry points
-  Updated test configuration from nose to pytest

   -  added many more tests for all export configurations and user
      interface
   -  fixed Mac Os build on Travis

-  Improved user interface
-  Added ipynb to python file (with commented metadata) exporter
-  Updated documentation with new API and how to convert plugins

Version 0.6
-----------

v0.6.7
~~~~~~

**Added support for raw cells**

Raw output is now included in the latex (if raw format is latex), and
html (if raw format is html)

v0.6.4
~~~~~~

Encoding Bug Fixes for Python < 3.6 and addition of documentation

v0.6.3
~~~~~~

Better support for LaTeX math environments

v0.6.2
~~~~~~

**Améliorations!**

-  added language translation
-  added width/height options for latex figures
-  changed embedded html to be iframes, with lazy loading for reveal
   slides
-  added titles and author for html and slides
-  bibtexparser uses “link” rather than “url” key (fixed)
-  fixed regex for headers (one or more # not zero or more)
-  allow codecells with no outputs
-  added ansi colors for latex listings
-  added adjust box for resizing tables too wide to fit in page width

v0.6.1
~~~~~~

Added output level metadata.
See :ref:`metadata_tags`

v0.6.0
~~~~~~

changed top-level meta tag from latex_doc -> ipub
(to reflect that it also applies to html/slides output)

also:

- improved control of slide output
- changed from using utf8x -> xelatex, for handling font encoding
- added mkdown output tag

Version 0.5
-----------

v0.5.3
~~~~~~

Small bug fix for html caption prefixing

-  moved html caption prefixing to LatexCaption, so that captions from
   other cells are prefixed

v0.5.2
~~~~~~

Slide autonumbering and captions from code output

v0.5.1
~~~~~~

Improvements to Slide Output and Smart Slide Creation:

- slide rows/columns partitioned by markdown headers
- improved latex listings default options for text & stream data

v0.5.0
~~~~~~

**Default Conversion Plugins & Enhancements to HTML/Slides Conversion**

-  added auto numbering and correct reference hyperlinks for
   figures/tables/equations/code in html & slides
-  added text meta-tag, default meta-tag post processor, and additional
   converters based on it
-  added embeddable html

Version 0.4
-----------

v0.4.1
~~~~~~

added universal bdist flag

v0.4.0
~~~~~~

Introduced nbpresent: for reveal.js slideshow creation and serving

- a lot of refactoring of html template creation improvement of command
  line argument processing introduction of preprocessors general
  awesomeness

Version 0.3
-----------

First full, tested pypi release!

Version 0.2
-----------

New Latex Metadata convention:

Now all under “latex_doc” key with no “latex\_” prefix , e.g.

.. code:: json

   {
   "latex_doc" : {
       "ignore": true
       }
   }

instead of:

.. code:: json

   {"latex_ignore": true}

Version 0.1
-----------

Initial release, before changing latex meta tag convention
