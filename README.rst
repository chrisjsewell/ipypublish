ipypublish
==========

**Project**: https://github.com/chrisjsewell/ipypublish

.. image:: https://travis-ci.org/chrisjsewell/ipypublish.svg?branch=master
    :target: https://travis-ci.org/chrisjsewell/ipypublish

A workflow for creating and editing publication ready scientific
reports, from one or more Jupyter Notebooks, without leaving the
browser!

.. image:: https://github.com/chrisjsewell/ipypublish/raw/master/example_workflow.gif

For an example of the potential input/output, see `Example.ipynb <https://github.com/chrisjsewell/ipypublish/raw/master/example/notebooks/Example.ipynb>`__ , `Example.pdf <https://github.com/chrisjsewell/ipypublish/raw/master/converted/Example.pdf>`__ and `Example.slides.html <https://chrisjsewell.github.io/ipypublish/Example.slides.html#/>`__.

Design Philosophy
-----------------

In essence, the dream is to have the ultimate hybrid of Jupyter
Notebook, WYSIWYG editor (e.g. MS Word) and document preparation system
(e.g. `TexMaker <http://www.xm1math.net/texmaker/>`__), being able to:

-  Dynamically (and reproducibly) explore data, run code and output the
   results
-  Dynamically edit and visualise the basic components of the document
   (text, math, figures, tables, references, citations, etc).
-  Have precise control over what elements are output to the final
   document and how they are layed out and typeset.

   -  Also be able to output the same source document to different
      layouts and formats (pdf, html, presentation slides, etc).

Workflow
--------

1. Create a notebook with some content!
2. optionally create a .bib file and logo image
3. Adjust the notebook and cell metadata.
4. Clone the ipypublish `GitHub
   repository <https://github.com/chrisjsewell/ipypublish>`__ and run
   the nbpublish.py script for either the specific notebook, or a folder
   containing multiple notebooks.
5. A converted folder will be created, into which final .tex .pdf and
   \_viewpdf.html files will be output, named by the notebook or folder
   input

The default latex template outputs all markdown cells (unless tagged
latex\_ignore), and then only code and output cells with `latex metadata
tags <#latex-metadata-tags>`__. See
`Example.ipynb <https://github.com/chrisjsewell/ipypublish/blob/master/example/notebooks/Example.ipynb>`__, 
`Example.pdf <https://github.com/chrisjsewell/ipypublish/blob/master/converted/Example.pdf>`__ and `Example.slides.html <https://chrisjsewell.github.io/ipypublish/Example.slides.html#/>`__
for an example of the potential input and output.

Setting up the environment
--------------------------

Using `Conda <https://conda.io/docs/>`__ is recommended for package
management, in order to create self contained environments with specific
versions of packages. The main external packages required are the Jupyter notebook, Jupyter
`nbconvert <https://nbconvert.readthedocs.io/en/latest/index.html>`__
and `Pandoc <http://pandoc.org>`__ (for conversion to latex):

::

    conda create --name ipyreport -c conda-forge jupyter pandoc

ipypublish can then be installed into this environment:

::

	source activate ipyreport
	pip install ipypublish

For converting to PDF, the TeX document preparation ecosystem is
required (an in particular
`latexmk <http://mg.readthedocs.io/latexmk.html>`__), which can be
installed from:

-  Linux: `TeX Live <http://tug.org/texlive/>`__
-  macOS (OS X): `MacTeX <http://tug.org/mactex/>`__
-  Windows: `MikTex <http://www.miktex.org/>`__

ipypublish is automatically **tested** on update against **python 2.7 and 3.6**, for both **Linux and OSX**, using `Travis CI <https://en.wikipedia.org/wiki/Travis_CI>`__. Therefore, to troubleshoot any installation/run issues, 
it is best to look at the `travis config <https://github.com/chrisjsewell/ipypublish/blob/master/.travis.yml>`__ 
and `travis test runs <https://travis-ci.org/chrisjsewell/ipypublish>`__ for working configurations.

For helpful extensions to the notebooks core capabilities (like a toc
sidebar):

::

    conda install --name ipyreport jupyter_contrib_nbextensions

A more extensive setup of useful packages (used to create the example)
are listed in conda\_packages.txt and an environment can be created
directly from this using conda:

::

    conda create --name ipyreport -c conda-forge -c matsci --file conda_packages.txt

Setting up a Notebook
---------------------

For improved latex/pdf output, ipynb\_latex\_setup.py
contains import and setup code for the notebook and a number of common
packages and functions, including:

-  numpy, matplotlib, pandas, sympy, ...
-  ``images_hconcat``, ``images_vconcat`` and ``images_gridconcat``
   functions, which use the PIL/Pillow package to create a single image
   from multiple images (with specified arrangement)

To use this script, in the first cell of a notebook, insert:

.. code:: python

    from ipypublish.scripts.ipynb_latex_setup import *

It is recommended that you also set this cell as an initialisation cell
(i.e. have ``"init_cell": true`` in the metadata)

Converting Notebooks
--------------------

The **nbpublish** script handles parsing the notebooks to nbconvert, with
the appropriate converter. To see all options for this script:

::

    nbpublish -h

For example, to convert the Example.ipynb notebook:

::

    nbpublish -pdf example/notebooks/Example.ipynb

If a folder is input, then the .ipynb files it contains are processed
and combined in 'natural' sorted order, i.e. 2\_name.ipynb before
10\_name.ipynb. By default, notebooks beginning '\_' are ignored.

All available converters are also listed by ``nbpublish -h``. Two of note are:

-  **latex\_ipypublish\_main** is the default and converts cells to latex
   according to metadata tags on an 'opt in' basis.
-  **latex\_standard\_article** replicates the standard latex article
   template, which comes with nbconvert.
-  **html\_ipypublish** converts the entire notebook(s) to html
   and adds a table of contents sidebar and a button to toggle 
   input code and output cells visible/hidden,
   with latex citations and references resolved.
-  **slides\_ipypublish** converts the notebook to
   `reveal.js <http://lab.hakim.se/reveal-js/#/>`__ slides, 
   with latex citations and references resolved. 
   See the Live Slideshows section for
   using **nbpresent** to serve these slides to a webbrowser. 

The current ``nbconvert --to pdf`` does not correctly resolve references
and citations (since it copies the files to a temporary directory).
Therefore nbconvert is only used for the initial
``nbconvert --to latex`` phase, followed by using ``latexmk`` to create
the pdf and correctly resolve everything.

Creating a bespoke converter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

nbconvert uses `Jinja
templates <https://jinja2.readthedocs.io/en/latest/intro.html>`__ to
specify the rules for how each element of the notebook should be
converted, and also what each section of the latex file should contain.
To create a `custom
template <https://nbconvert.readthedocs.io/en/latest/customizing.html#Custom-Templates>`__
they employ an inheritance method to build up this template. However, in
my experience this makes it;

1. non-trivial to understand the full conversion process (having to go
   through the inheritance tree to find where particular methods have
   been implemented/overriden)
2. difficult to swap in/out multiple rules

To improve this, ipypublish implements a pluginesque system to
systematically append to blank template placeholders. For example, to
create a document (with standard formatting) with a natbib bibliography
where only input markdown is output, we could create the following
dictionary:

.. code:: python


    my_tplx_dict = { 
    'meta_docstring':'with a natbib bibliography',

    'notebook_input_markdown':r"""
        ((( cell.source | citation2latex | strip_files_prefix | convert_pandoc('markdown', 'json',extra_args=[]) | resolve_references | convert_pandoc('json','latex') )))
    """,

    'document_packages':r"""
        \usepackage[numbers, square, super, sort&compress]{natbib}
        \usepackage{doi} % hyperlink doi's  
    """,

    'document_bibliography':r"""
    \bibliographystyle{unsrtnat} % sort citations by order of first appearance
    \bibliography{bibliography}
    """

    }

The converter would then look like this:

.. code:: python


    from ipypublish.latex.create_tplx import create_tplx
    from ipypublish.latex.standard import standard_article as doc
    from ipypublish.latex.standard import standard_definitions as defs
    from ipypublish.latex.standard import standard_packages as package

    oformat = 'Latex'
    template = create_tplx([package.tplx_dict,defs.tplx_dict,
                 doc.tplx_dict,my_tplx_dict])

    config = {'TemplateExporter.filters':{},
              'Exporter.filters':{}}

Latex Metadata Tags
-------------------

All information additional information, used to specify how a particular
notebook/cell in latex is represented, is stored in the metadata under:

.. code:: json

    {
            "latex_doc": {}
    }

Document Tags
~~~~~~~~~~~~~

To specify where the **bibliography** is:

.. code:: json

    {
    "latex_doc": {
        "bibliography" : "path/to/bibliograph.bib"
        }
    }

The path can be absolute or relative.

For **titlepage**, enter in notebook metadata:

.. code:: json

    {
    "latex_doc": {
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

-  all keys are optional
-  if there is no title, then the notebook filename will be used
-  if nbpublish.py is called on a folder, then the meta data from the
   first notebook will be used
-  logo should be the path (absolute or relative) to a logo image file

To control the output of **contents tables**:

.. code:: json

    {
    "latex_doc": {
      "toc": true,
      "listfigures": true,
      "listtables": true,
      "listcode": true,
      }
    }

To override the default **placement of figures and tables**:

.. code:: json

    {
    "latex_doc": {
        "figure": {
          "placement": "!bp"
          },
        "table": {
          "placement": "!bp"
          }
      }
    }

See
`Positioning\_images\_and\_tables <https://www.sharelatex.com/learn/Positioning_images_and_tables>`__
for placement options.

Cell Tags
~~~~~~~~~

To **ignore any cell**:

.. code:: json

    {
    "latex_doc": {
        "ignore" : true
        }
    }

To **output a code block**:

.. code:: json

    {
    "latex_doc": {
      "code": {
        "asfloat": true,
        "caption": "",
        "label": "code:example_sym",
        "widefigure": false,
        "placement": "H"
        }
      }
    }

all extra tags are optional:

-  ``asfloat`` contitutes whether the code is wrapped in a codecell
   (float) environment or is inline.
-  all other tags work the same as figure (below).

For **figures**, enter in cell metadata:

.. code:: json

    {
    "latex_doc": {
      "figure": {
        "caption": "Figure caption.",
        "label": "fig:flabel",
        "placement": "H",
        "widefigure": false
        }
      }
    }

-  ``placement`` is optional and constitutes using a placement arguments
   for the figure (e.g. \\begin{figure}[H]). See
   `Positioning\_images\_and\_tables <https://www.sharelatex.com/learn/Positioning_images_and_tables>`__.
-  ``widefigure`` is optional and constitutes expanding the figure to
   the page width (i.e. \\begin{figure\*}) (placement arguments will
   then be ignored)

For **tables**, enter in cell metadata:

.. code:: json

    {
    "latex_doc": {
         "table": {
            "caption": "Table caption.",
            "label": "tbl:tlabel",
            "placement": "H",
                "alternate": "gray!20"
          }
       }
    }

-  ``placement`` is optional and constitutes using a placement arguments
   for the table (e.g. \\begin{table}[H]). See
   `Positioning\_images\_and\_tables <https://www.sharelatex.com/learn/Positioning_images_and_tables>`__.
-  ``alternate`` is optional and constitutes using alternating colors
   for the table rows (e.g. \rowcolors{2}{gray!25}{white}).
   See https://tex.stackexchange.com/a/5365/107738.

For **equations**, enter in cell metadata:

.. code:: json

    {
      "latex_doc": {
          "equation": {
            "label": "eqn:elabel"
          }
      }
    }

label is optional

Captions in a Markdown cell
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Especially for long captions, it would be prefered that they can be
viewed and edited in a notebook Markdown cell, rather than hidden in the
metadata. This can be achieved using the default latex template:

If a **markdown input** or **latex output** cell has the metadata tag:

.. code:: json

    {
     "latex_doc": {
        "caption": "fig:example_mpl"
        }
    }

Then, instead of it being input directly into the .tex file, it will be
stored as a variable;

-  the variable's name is created from the latex\_caption value
-  the variable's value is the first paragraph of the markdown text
   (i.e. nothing after a `\n`)

If a subsequent **figure, table or code** cell has a label matching any
stored variable name, for example:

.. code:: json

    {
    "latex_doc": {
        "figure": {
        "caption": "",
        "label": "fig:example_mpl"
        }
      }
    }

Then its caption will be overriden with that variable.

The manner in which this works can be found in
`Example.tex <https://github.com/chrisjsewell/ipypublish/blob/master/converted/>`__:

.. code:: latex

    \newcommand{\kyfigcexampleumpl}{A matplotlib figure, with the caption set in the markdowncell above the figure.}

    \begin{figure}
        \begin{center}\adjustimage{max size={0.9\linewidth}{0.4\paperheight}}{Example_files/Example_14_0.pdf}\end{center}
        \ifdefined\kyfigcexampleumpl
        \caption{\kyfigcexampleumpl}
        \else
        \caption{}
        \fi
        \label{fig:example_mpl}
    \end{figure}

Note, this approach has the implicit contraint that caption cells must
be above the corresponding figure/table to be output in the latex/pdf.

Citations and Bibliography
--------------------------

Using Zotero's Firefox plugin and `Zotero Better
Bibtex <https://github.com/retorquere/zotero-better-bibtex/releases/tag/1.6.100>`__
for;

-  automated .bib file updating
-  drag and drop cite keys
   ``\cite{kirkeminde_thermodynamic_2012}``
-  ``latexmk -bibtex -pdf`` (in nbpublish.py) handles creation of the
   bibliography
-  ``\usepackage{doi}`` turns the DOI numbers into url links

   -  in Zotero-Better-Bibtex I have the option set to only export DOI,
      if both DOI and URL are present.

Please note, at the time of writing, Better BibTeX does not support
Zotero 5.0
(`issue#555 <https://github.com/retorquere/zotero-better-bibtex/issues/555>`__).
For now I have turned off auto-updates of Zotero, though this is
probably not wise for long (`Zotero 5
Discussion <https://forums.zotero.org/discussion/comment/277434/#Comment_277434>`__).

Can use:

.. code:: html

    <cite data-cite="kirkeminde_thermodynamic_2012">(Kirkeminde, 2012)</cite> 

to make it look better in html, but not specifically available for drag
and drop in Zotero

Live Slideshows
---------------

The **nbpresent** script handles serving `reveal.js <http://lab.hakim.se/reveal-js/#/>`__ slides to a webbrowser. To see all options for this script:

::

	nbpresent -h
	
Note that, **for offline use**, simply download the lates version of reveal.js `here <https://github.com/hakimel/reveal.js/releases>`__, rename the entire folder to reveal.js and place it in the same folder as the converted .slides.html file.

The `Reveal.js - Jupyter/IPython Slideshow Extension
(RISE) <https://github.com/damianavila/RISE>`__ notebook extension
offers rendering as a Reveal.js-based slideshow, where you can execute
code or show to the audience whatever you can show/do inside the
notebook itself!


Dealing with external data
--------------------------

A goal for scientific publishing is automated reproducibility of
analyses, which the Jupyter notebook excels at. But, more than that, it
should be possible to efficiently reproduce the analysis with different
data sets. This entails having **one point of access** to a data set
within the notebook, rather than having copy-pasted data into variables,
i.e. this:

.. code:: python

    data = read_in_data('data_key')
    variable1 = data.key1
    variable2 = data.key2
    ...

rather than this:

.. code:: python

    variable1 = 12345
    variable2 = 'something'
    ...

The best-practice for accessing heirarchical data (in my opinion) is to
use the JSON format (as long as the data isn't
`relational <http://www.sarahmei.com/blog/2013/11/11/why-you-should-never-use-mongodb/>`__),
because it is:

-  applicable for any data structure
-  lightweight and easy to read and edit
-  has a simple read/write mapping to python objects (using
   `json <https://docs.python.org/3.6/library/json.html>`__)
-  widely used (especially in web technologies)

A good way to store multiple bits of JSON data is in a
`mongoDB <https://docs.mongodb.com/manual/administration/install-community/>`__
and accessing it via
`pymongo <https://api.mongodb.com/python/current/>`__. This will also
make it easy to move all the data to a cloud server at a later time, if
required.

::

    conda install pymongo

But, if the data is coming from files output from different simulation
or experimental code, where the user has no control of the output
format. Then writing JSON parsers may be the way to go, and this is
where `jsonextended <https://github.com/chrisjsewell/jsonextended>`__
comes in, which implements:

-  a lightweight plugin system to define bespoke classes for parsing
   different file extensions and data types.
-  a 'lazy loader' for treating an entire directory structure as a
   nested dictionary.

For example:

.. code:: python

    from jsonextended import plugins, edict
    plugins.load_plugins_dir('path/to/folder_of_parsers','parsers')
    data = edict.LazyLoad('path/to/data')
    variable1 = data.folder1.file1_json.key1
    variable2 = data[['folder1','file1.json','key2']]
    variable3 = data[['folder1','file2.csv','key1']]
    variable4 = data[['folder2','subfolder1','file3.other','key1']]
    ...    

If you are dealing with numerical data arrays which are to large to be
loaded directly in to memory, then the
`h5py <http://docs.h5py.org/en/latest/index.html>`__ interface to the
`HDF5 <http://hdfgroup.org/>`__ binary data format, allows for the
manipultion of even multi-terabyte datasets stored on disk, as if they
were real NumPy arrays. These files are also supported by
`jsonextended <https://github.com/chrisjsewell/jsonextended>`__ lazy
loading.

Miscellaneous
-------------

I also use the Firefox Split Pannel extension to view the
{name}\_viewpdf.html page and monitor changes to the pdf.

`bookbook <https://github.com/takluyver/bookbook>`__ is another package
with some conversion capabilities.

Acknowledgements
----------------

I took strong influence from:

-  `Julius
   Schulz <http://blog.juliusschulz.de/blog/ultimate-ipython-notebook>`__
-  `Dan
   Mackinlay <https://livingthing.danmackinlay.name/jupyter.html>`__
-  Notebook concatination was adapted from `nbconvert
   issue#253 <https://github.com/jupyter/nbconvert/issues/253>`__

