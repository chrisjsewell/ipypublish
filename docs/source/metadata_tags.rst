.. _metadata_tags:

Metadata Tags
=============

Introduction
------------

All additional information, used to specify how a particular
notebook/cell/output will be represented, when converted, is stored in
the metadata under:

.. code:: json

   {
       "ipub": {}
   }

.. figure:: _static/metadata_edit.gif
    :align: center
    :height: 200px
    :alt: editing metadata
    :figclass: align-center

There are three levels of metadata:

-  For notebook level: in the Jupyter Notebook Toolbar go to Edit ->
   Edit Notebook Metadata
-  For cell level: in the Jupyter Notebook Toolbar go to View -> Cell
   Toolbar -> Edit Metadata and a button will appear above each cell.
-  For output level: using
   ``IPython.display.display(obj,metadata={"ipub":{}})``, you can set
   metadata specific to a certain output. Options set at the output
   level will override options set at the cell level. For an example of
   this, see :ref:`multiple_outputs`.

.. important::

    setting a value to ``"value":{}`` is the same as ``"value":false`` so,
    if you are not setting additional options, use ``"value":true``.

.. seealso::

    :ref:`nbformat:notebook_file_format`

    :ref:`jupytext_python`


Document Level
--------------

The full schema can be viewed at :ref:`meta_doclevel_schema`.

Language
~~~~~~~~

To change the **language** of the document:

.. code:: json

   {
   "ipub": {
     "language" : "french"
     }
   }

where the language can be any specified in the
`babel <https://ctan.org/pkg/babel>`__ package.

Bibliography
~~~~~~~~~~~~

To specify where the **bibliography** is and choose a style:

.. code:: json

   {
   "ipub": {
     "bibliography" : "path/to/bibliograph.bib",
     "bibstyle": "unsrtnat",
     "biboptions": ["super", "sort"],
     }
   }

-  The path can be absolute or relative.
-  The ``bibstyle`` must be a `natbib
   stylename <https://www.overleaf.com/learn/latex/Natbib_bibliography_styles>`__

.. versionadded:: 0.7.1

  - The ``biboptions`` is a list of options to parse
    to `natbib <https://ctan.org/pkg/natbib?lang=en>`_.
    The default is: ["numbers", "square", "super", "sort&compress"], and some
    common options are:

    - *round*: (default) for round parentheses;
    - *square*: for square brackets;
    - *curly*: for curly braces;
    - *angle*: for angle brackets;
    - *colon*: (default) to separate multiple citations with colons;
    - *comma*: to use commas as separators;
    - *authoryear*: (default) for author-year citations;
    - *numbers*: for numerical citations;
    - *super*: for superscripted numerical citations, as in Nature;
    - *sort*: orders multiple citations into the sequence
      in which they appear in the list of references;
    - *sort&compress*: as sort but in addition multiple numerical citations are
      compressed if possible (e.g. 3-6, 15);
    - *longnamesfirst*: makes the first citation of any reference the equivalent
      of the starred variant (full author list) and subsequent citations normal
      (abbreviated list);


Title Page
~~~~~~~~~~

For **titlepage**, enter in notebook metadata:

.. code:: json

   {
   "ipub": {
     "titlepage": {
     "author": "Authors Name",
     "email": "authors@email.com",
     "supervisors": [
       "First Supervisor",
       "Second Supervisor"
     ],
     "title": "Main-Title",
     "subtitle": "Sub-Title",
     "tagline": "A tagline for the report.",
     "institution": [
       "Institution1",
       "Institution2"
     ],
     "logo": "path/to/logo_example.png"
     }
     }
   }

-  all keys are optional
-  if there is no title, then the notebook filename will be used
-  if nbpublish.py is called on a folder, then the meta data from the
   first notebook will be used
-  logo should be the path (absolute or relative) to a logo image file

Contents Tables
~~~~~~~~~~~~~~~

To control the output of **contents tables**:

.. code:: json

   {
   "ipub": {
     "toc": true,
     "listfigures": true,
     "listtables": true,
     "listcode": true
     }
   }

.. versionadded:: v0.8.3

    You can now control the depth of the contents table:

.. code:: json

    {
    "ipub": {
      "toc": {"depth": 2}
      }
    }


Figures and Tables
~~~~~~~~~~~~~~~~~~

To override the default **placement of figures and tables**:

.. code:: json

   {
   "ipub": {
       "figure": {
         "placement": "!bp"
         },
       "table": {
         "placement": "!bp"
         }
     }
   }

See
`Positioning_images_and_tables <https://www.sharelatex.com/learn/Positioning_images_and_tables>`__
for placement options.

.. _pandoc_doc_metadata:


Adding a stylesheet to slides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For **slide output**, the following notebook-level metadata:

.. code:: json

   {
     "ipub": {
       "customcss": "mystylesheet.css"
     }
   }

will link the additional stylesheet `mystylesheet` in the resulting html.  This can be used, for example, to display a log on each slide.

Pandoc Markdown Conversion
~~~~~~~~~~~~~~~~~~~~~~~~~~

To control how the ipypandoc filters convert markdown cells,
the following options are available:

.. code:: json

   {
   "ipub": {
       "sphinx": {
          "apply_filters": true,
          "convert_raw": true,
          "hide_raw": false,
          "at_notation": true,
          "use_numref": true,
          "reftag": "cite"
         }
     }
   }

.. seealso::

    :ref:`markdown_cells`

.. _sphinx_doc_metadata:

Sphinx Output Control
~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    :ref:`sphinx_ext_notebook`, for documentation on the Sphinx extension.

To suppress the output of a bibliography or glossary:

.. code:: json

   {
   "ipub": {
       "sphinx": {
          "no_bib": true,
          "no_glossary": true
         }
     }
   }

To change the title text of the bibliography and glossary:

.. code:: json

   {
   "ipub": {
       "sphinx": {
          "bib_title": "My Title",
          "glossary_title": "My Title"
         }
     }
   }


To control the addition of toggle buttons for code/output cells:

.. code:: json

   {
   "ipub": {
       "sphinx": {
          "toggle_input": true,
          "toggle_output": true,
          "toggle_input_all": true,
          "toggle_output_all": true
         }
     }
   }

To denote the notebook as an orphan (i.e. not required in an index):

.. code:: json

   {
   "ipub": {
       "sphinx": {
          "orphan": true
         }
     }
   }

Cell/Output Level
-----------------

The full schema can be viewed at :ref:`meta_celllevel_schema`.

Ignore
~~~~~~

To **ignore any cell** for all outputs:

.. code:: json

   {
   "ipub": {
     "ignore" : true
     }
   }

To mark any cell as for output to **slides only**:

.. code:: json

   {
   "ipub": {
     "slideonly" : true
     }
   }

Code Block
~~~~~~~~~~

To **output a code block**:

.. code:: json

   {
   "ipub": {
     "code": {
       "format" : {},
       "asfloat": true,
       "caption": "",
       "label": "code:example_sym",
       "widefigure": false,
       "placement": "H"
       }
     }
   }

all extra tags are optional:

-  ``format`` can contain any keywords related to the latex
   `Listings <https://en.wikibooks.org/wiki/LaTeX/Source_Code_Listings>`__
   package (such as syntax highlighting colors)
-  ``asfloat`` contitutes whether the code is wrapped in a codecell
   (float) environment or is inline.
-  all other tags work the same as figure (below).

Output Text
~~~~~~~~~~~

To **output text produced by the code** (e.g. *via* the ``print``
command):

.. code:: json

   {
   "ipub": {
     "text": {
        "format": {
          "basicstyle": "\\small"
        },
        "asfloat": true,
        "caption": "",
        "label": "code:example_sym",
        "widefigure": false,
        "placement": "H",
        "use_ansi": false
       }
     }
   }

all extra tags are optional:

-  ``format`` can contain any keywords related to the latex
   `Listings <https://en.wikibooks.org/wiki/LaTeX/Source_Code_Listings>`__
   package (such as syntax highlighting colors). N.B. in place of ``\``
   use ``\\``.
-  ``asfloat`` contitutes whether the code is wrapped in a codecell
   (float) environment or is inline.
-  if ``use_ansi`` is true then, instead of stripping ansi colors in
   latex output, they will be converted to latex, wrapped in %
   characters and the listings option escapechar=% set.
-  all other tags work the same as figure (below).

Output Figures
~~~~~~~~~~~~~~

For **figures** (i.e. any graphics output by the code), enter in cell
metadata:

.. code:: json

   {
   "ipub": {
     "figure": {
       "caption": "Figure caption.",
       "label": "fig:flabel",
       "placement": "H",
       "height":0.4,
       "widefigure": false
       }
     }
   }

-  all tags are optional
-  height/width correspond to the fraction of the page height/width,
   only one should be used (aspect ratio will be maintained
   automatically)
-  ``placement`` is optional and constitutes using a placement arguments
   for the figure (see
   `Positioning_images_and_tables <https://www.sharelatex.com/learn/Positioning_images_and_tables>`__).

   .. code-block:: latex

      \begin{figure}[H]

-  ``widefigure`` is optional and constitutes expanding the figure to
   the page width (placement arguments will then be ignored)

   .. code-block:: latex

      \begin{figure*}

Output Tables
~~~~~~~~~~~~~

For **tables** (e.g. those output by ``pandas``), enter in cell
metadata:

.. code:: json

   {
    "ipub": {
        "table": {
         "caption": "Table caption.",
         "label": "tbl:tlabel",
         "placement": "H",
         "alternate": "gray!20"
       }
     }
   }

-  ``caption`` and ``label`` are optional
-  ``placement`` is optional and constitutes using a placement arguments
   for the table (see
   `Positioning_images_and_tables <https://www.sharelatex.com/learn/Positioning_images_and_tables>`__).

   .. code-block:: latex

      \begin{table}[H]

-  ``alternate`` is optional and constitutes using alternating colors
   for the table rows (see https://tex.stackexchange.com/a/5365/107738).

   .. code-block:: latex

      \rowcolors{2}{gray!25}{white}

-  if tables exceed the text width, in latex, they will be shrunk to fit

Output Equations
~~~~~~~~~~~~~~~~

For **equations** (e.g. those output by ``sympy``), enter in cell
metadata:

.. code:: json

   {
     "ipub": {
       "equation": {
           "environment": "equation",
           "label": "eqn:elabel"
       }
     }
   }

-  environment is optional and can be ‘none’ or any of those available
   in
   `amsmath <https://www.sharelatex.com/learn/Aligning_equations_with_amsmath>`__;
   ‘equation’, ‘align’,‘multline’,‘gather’, or their \* variants.
   Additionaly, ‘breqn’ or ‘breqn\*’ will select the experimental
   `breqn <https://ctan.org/pkg/breqn>`__ environment to *smart* wrap
   long equations.
-  label is optional and will only be used if the equation is in an
   environment

Controlling Slides
~~~~~~~~~~~~~~~~~~

For **slide output**:

.. code:: json

   {
     "ipub": {
       "slide": true
     }
   }

-  the value of slide can be true, “new” (to indicate the start of a new
   slide) or “notes”

Specifying the start section number in slide-shows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For **slide output**:

.. code:: json

    {
        "toc": {
            "base_numbering": "3",
        }
    }

-   the above will set the first section number to 3 rather than 1

-   note that the top-level key is "toc", and *not* "ipub"; this allows
    the starting section number to be configured using the
    `toc2 notebook extension <https://github.com/ipython-contrib/jupyter_contrib_nbextensions/tree/master/src/jupyter_contrib_nbextensions/nbextensions/toc2>`__

Captions in a Markdown cell
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Especially for long captions, it would be prefered that they can be
viewed and edited in a notebook Markdown cell, rather than hidden in the
metadata. This can be achieved using the default ipypublish converters:

If a **markdown cell** or **code cell with latex/text output** has the
metadata tag:

.. code:: json

   {
    "ipub": {
      "caption": "fig:example_mpl"
     }
   }

Then, during the the postprocessor stage, this cell will be removed from
the notebook object, and its text stored as a *resource*;

-  the cell’s text is the first paragraph of the markdown string,
   i.e. nothing after a newline (:code:`\n`)
-  if there are multiple instance of the same cation name, then only the
   last instance will be stored

During the jinja templating, if a **figure, table or code** cell has a
label matching any stored caption name, for example:

.. code:: json

   {
     "ipub": {
       "figure": {
         "caption": "",
         "label": "fig:example_mpl"
       }
     }
   }

Then its caption will be overriden with the stored text.

Embedding Interactive HTML
~~~~~~~~~~~~~~~~~~~~~~~~~~

Packages built on `IPywidgets <http://ipywidgets.readthedocs.io>`__,
like `PythreeJS <https://github.com/jovyan/pythreejs>`__,
`Pandas3JS <https://github.com/chrisjsewell/pandas3js>`__ and the
excellent `IPyvolume <https://ipyvolume.readthedocs.io/en/latest/>`__,
are making it increasingly easier to render complex, interactive html in
the notebook. IPywidgets offers a `save notebook with
widgets <http://ipywidgets.readthedocs.io/en/latest/embedding.html>`__
feature, however, this can greatly increase the size of the notebook.

A better solution, recently offered, is to save a `html
snippet <http://ipywidgets.readthedocs.io/en/latest/embedding.html#embeddable-html-snippet>`__
of the current widget state to file and embed it into the html/slides
output as an iframe. This is also particularly useful in reveal.js
slides, since the iframe content can be `lazy
loaded <https://github.com/hakimel/reveal.js/#lazy-loading>`__. To embed
html, use the ``embed_html`` tag:

.. code:: json

   {
     "ipub": {
       "embed_html": {
         "filepath": "path/to/file.html",
         "other_files": ["path/to/file.js"],
         "url": "https//path/to/url.html",
         "width":0.5,
         "height":0.5
       },
       "figure": {
         "caption": "An example of embedded html"
       }
     }
   }

If the cell already contains an output, then this tag will
create/overwrite the first output’s “text/html” type. This allows for a
single notebook cell with a static image of the widget in the output,
and a path to the embed html in the metadata so that a) if you export to
latex/pdf, you get the static image or b) if you export to html/reveal
slides, you get the html.

-  use either filepath or url
-  other_files are files required by the html file (e.g. javascript
   libraries). These files will be copied to the the same folder as the
   html
-  width/height refers to the fraction of the viewspace used (e.g. 0.5
   width -> 50vw and 0.5 height -> 50vh)

An example of how this works is in the
`Example.ipynb <example/notebooks/Example.pdf>`__, and the
`Example.html <https://chrisjsewell.github.io/ipypublish/Example.html#Embedded-HTML-6>`__
and
`Example.slides.html <https://chrisjsewell.github.io/ipypublish/Example.slides.html#/9>`__
outputs.
