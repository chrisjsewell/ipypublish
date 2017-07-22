[![Build Status](https://travis-ci.org/chrisjsewell/ipypublish.svg?branch=master)](https://travis-ci.org/chrisjsewell/ipypublish)
[![Coverage Status](https://coveralls.io/repos/github/chrisjsewell/ipypublish/badge.svg?branch=master)](https://coveralls.io/github/chrisjsewell/ipypublish?branch=master)
[![PyPI](https://img.shields.io/pypi/v/ipypublish.svg)](https://pypi.python.org/pypi/ipypublish/)

# ipypublish
A workflow for creating and editing publication ready scientific reports and presentations, from one or more Jupyter Notebooks, without leaving the browser!

![WorkFlow Example](/example_workflow.gif)

See [Example.ipynb](example/notebooks/Example.pdf), [Example.pdf](https://chrisjsewell.github.io/ipypublish/Example.view_pdf.html),
[Example.html](https://chrisjsewell.github.io/ipypublish/Example.html) and 
[Example.slides.html](https://chrisjsewell.github.io/ipypublish/Example.slides.html#/) for an example of the potential input/output.

- [Design Philosophy](#design-philosophy)
- [Workflow](#worklow)
- [Setting up the environment](#setting-up-the-environment)
- [Setting up a Notebook ](#setting-up-a-notebook)
- [Converting Notebooks](#converting-notebooks)
    - [Creating a bespoke converter](#creating-a-bespoke-converter)
- [Metadata Tags](#metadata-tags)
    - [Captions in a Markdown cell](#captions-in-a-markdown-cell)
	- [Embedding Interactive HTML](#embedding-interactive-html)
- [Citations and Bibliography](#citations-and-bibliography)
- [Live Slideshows](#live-slideshows)
- [Dealing with external data](#dealing-with-external-data)
- [Miscellaneous](#miscellaneous)
- [Acknowledgements](#acknowledgements)


## Design Philosophy

In essence, the dream is to have the ultimate hybrid of Jupyter Notebook, WYSIWYG editor (e.g. MS Word) and document preparation system (e.g. [TexMaker](http://www.xm1math.net/texmaker/)), being able to:

- Dynamically (and reproducibly) explore data, run code and output the results
- Dynamically edit and visualise the basic components of the document (text, math, figures, tables, references, citations, etc).
- Have precise control over what elements are output to the final document and how they are layed out and typeset.
     - Also be able to output the same source document to different layouts and formats (pdf, html, presentation slides, etc).

## Workflow

1. Create a notebook with some content!
2. optionally create a .bib file and external images
3. Adjust the notebook and cell metadata. 
4. install ipypublish and run the `nbpublish` for either the specific notebook, or a folder containing multiple notebooks. 
5. A converted folder will be created, into which final .tex .pdf and _viewpdf.html files will be output, named by the notebook or folder input

The default latex template outputs all markdown cells (unless tagged latex_ignore), and then only code and output cells with [latex metadata tags](#latex-metadata-tags). 
See [Example.ipynb](https://github.com/chrisjsewell/ipypublish/blob/master/example/notebooks/Example.ipynb), [Example.pdf](https://chrisjsewell.github.io/ipypublish/Example.view_pdf.html),
[Example.html](https://chrisjsewell.github.io/ipypublish/Example.html) and [Example.slides.html](https://chrisjsewell.github.io/ipypublish/Example.slides.html#/) for examples of the potential input and output.

## Setting up the environment

Using [Conda](https://conda.io/docs/) is recommended for package management, 
in order to create self contained environments with specific versions of packages. 
The main external packages required are the Jupyter notebook, and [Pandoc](http://pandoc.org) (for conversion of file formats):

	conda create --name ipyreport -c conda-forge jupyter pandoc
	
ipypublish can then be installed into this environment:

	source activate ipyreport
	pip install ipypublish
	
For converting to PDF, the TeX document preparation ecosystem is required (an in particular [latexmk](http://mg.readthedocs.io/latexmk.html)), which can be installed from:

- Linux: [TeX Live](http://tug.org/texlive/)
- macOS (OS X): [MacTeX](http://tug.org/mactex/)
- Windows: [MikTex](http://www.miktex.org/)

ipypublish is automatically **tested** on update against **python 2.7 and 3.6**, for both **Linux and OSX**, using [Travis CI](https://en.wikipedia.org/wiki/Travis_CI). Therefore, to troubleshoot any installation/run issues, 
it is best to look at the [travis config](https://github.com/chrisjsewell/ipypublish/blob/master/.travis.yml) 
and [travis test runs](https://travis-ci.org/chrisjsewell/ipypublish) for working configurations.

For helpful extensions to the notebooks core capabilities (like a toc sidebar):

	conda install --name ipyreport jupyter_contrib_nbextensions
	
A more extensive setup of useful packages (used to create the example) 
are listed in ![conda_packages.txt](conda_packages.txt) 
and an environment can be created directly from this using conda:

	conda create --name ipyreport -c conda-forge -c matsci --file conda_packages.txt
	
## Setting up a Notebook 

For improved latex/pdf output, `ipynb_latex_setup.py` contains import and setup code for the notebook and a number of common packages and functions, including:

- numpy, matplotlib, pandas, sympy, ...
- `images_hconcat`, `images_vconcat` and `images_gridconcat` functions, which use the PIL/Pillow package to create a single image from multiple images (with specified arrangement)

To use this script, in the first cell of a notebook, insert:

```python
from ipypublish.scripts.ipynb_latex_setup import *
```

It is recommended that you also set this cell as an initialisation cell (i.e. have `"init_cell": true` in the metadata)

For existing notebooks: the **nb_ipypublish_all** and **nb_ipypublish_nocode** converters (see below) can be helpful for outputting a notebook, with identical content to that input, but with default metatags defining how content is to be output.

## Converting Notebooks

The nbpublish script handles parsing the notebooks to nbconvert, with the appropriate converter. To see all options for this script:

	nbpublish -h

For example, to convert the Example.ipynb notebook directly to pdf:

	nbpublish -pdf example/notebooks/Example.ipynb

If a folder is input, then the .ipynb files it contains are processed and combined in 'natural' sorted order, i.e. 2_name.ipynb before 10_name.ipynb. By default, notebooks beginning '_' are ignored.

All available converters are also listed by `nbpublish -h`. Three of note are:

- **latex_ipypublish_main_** is the **default** and converts cells to latex according to metadata tags on an 'opt in' basis. Note that, for this converter, **no code cells or output** will appear in the final tex/pdf document unless they have a suitable [latex_doc metadata tag](#latex-metadata-tags).
- **html_ipypublish_main** converts the entire notebook(s) to html and adds a table of contents sidebar and a button to toggle input code and output cells visible/hidden, with latex citations and references resolved. 
- **slides_ipypublish_main** converts the notebook to [reveal.js](http://lab.hakim.se/reveal-js/#/) slides, with latex citations and references resolved and slide partitioning by markdown headers. See the [Live Slideshows](#live-slideshows) section for using `nbpresent` to serve these slides to a webbrowser. 
- The **all** and **nocode** variants of these converters preprocess a copy of the notebook, to add default metadata tags to the notebook and all cells, such that all output is rendered (with or without the code)

The current `nbconvert --to pdf` does not correctly resolve references and citations (since it copies the files to a temporary directory). Therefore nbconvert is only used for the initial `nbconvert --to latex` phase, followed by using `latexmk` to create the pdf and correctly resolve everything.

### Creating a bespoke converter

On instatiation, ipypublish loads all converter plugins in its internal [export_plugins](https://github.com/chrisjsewell/ipypublish/tree/master/ipypublish/export_plugins) folder. Additionally, when `nbpublish` or `nbpresent` are called, if a folder named **ipypublish_plugins** is present in the current working directory, they will load all plugins in this folder. Programatically, it is the `ipypublish.export_plugins.add_directory` function which is being called and adding modules to an internal dictionary.

The simplest application of this, would be to copy the [latex_ipypublish_all.py](https://github.com/chrisjsewell/ipypublish/blob/master/ipypublish/export_plugins/latex_ipypublish_all.py) file (or the html/slides variants) and make changes to the `cell_defaults` and `nb_defaults` dictionaries to suit your output needs.

A plugin is a python (.py) file with at least the following four variables (i.e. it's interface spec):

1. a **docstring** describing its output format
2. an **oformat** string,  specifying a base exporter prefix (for any of the exporters listed [here](https://nbconvert.readthedocs.io/en/latest/api/exporters.html#specialized-exporter-classes))
3. a **config** dictionary, containing any configuration option (as a string) listed [here](https://nbconvert.readthedocs.io/en/latest/api/exporters.html#specialized-exporter-classes). This is mainly to supply preprocessors (which act on the notbook object before it is parsed) or filters (which are functions supplied to the jinja template).
4. a **template** string, specifying the [Jinja templates](https://jinja2.readthedocs.io/en/latest/intro.html), which contains rules for how each element of the notebook should be converted, and also what each section of the latex file should contain. 
5. It is not required, but recommended, to also include the version number of ipypublish which the plugin was written for.

So a simple plugin would look like this (create_tplx will be explained below) 

```python
"""this exporter exports a .tex file with nothing in it
"""
from ipypublish.latex.create_tplx import create_tplx
oformat = 'Latex'
config = {}
template = create_tplx()

```

This is similar to how nbconvert works, except for one key difference, 
the plugin must specify the entire jinja template (rather than using a default one).
The advantage of this, is that the plugin has complete control over the look of the final document.

To aid in the creation of the jinja template, the `create_tplx` (for latex) and `create_tpl` (for html) functions
work by creating an inital *skeleton* template, with placeholders in all the relevant [structural blocks](https://nbconvert.readthedocs.io/en/latest/customizing.html#Template-structure). 
They then take a list of *fragment* dictionaries which progressively append input to the relevant blocks. 
So, for instance:   

```python
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

```

This approach allows independant aspects of the document to be 
stored separately then pieced together in the desired manner. 
ipypublish stores all of the standard fragments in separate modules,
for instance the latex_standard_article plugin looks like this: 

```python
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

```

Now, if you wanted mainly the same output format but without input and output prompts shown,
simply copy this plugin but remove the prompts.tplx_dict.

By default, sections are appended to, so;

```python
dict1 = {'notebook_input':'a'}
dict2 = {'notebook_input':'b'}
template = create_tplx([dict1,dict2])
```

would show a, then b. But, if you want to redefine a particular section(s);

```python
dict1 = {'notebook_input':'a'}
dict2 = {
	'overwrite':['notebook_input'],
	'notebook_input':'b'}
template = create_tplx([dict1,dict2])
```

will only show b.

Note that, the `create_tpl` template additionally has *pre* and *post* placeholder. 
This is helpful for wrapping cells in extra html tags. For instance:

```python

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

```

will result in a template containing:

```html
<div class="outer">
<div class="inner">
test
</div>
</div>
```

## Metadata Tags

All information additional information, used to specify how a particular notebook/cell will be represented
when converted, is stored in the metadata under:

```json
{
		"latex_doc": {}
}
```

To access metadata, in the Jupyter Notebook Toolbar:

- For notebook level: go to Edit -> Edit Notebook Metadata
- For cell level: go to View -> Cell Toolbar -> Edit Metadata and a button will appear above each cell.

**Please note**, setting a value to `"value":{}` is the same as `"value":false` so,
if you are not setting additional options, use `"value":true`.

### Document Tags

To specify where the **bibliography** is:

```json
{
"latex_doc": {
	"bibliography" : "path/to/bibliograph.bib"
	}
}
```

The path can be absolute or relative.

For **titlepage**, enter in notebook metadata:

```json
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
}
```

- all keys are optional
- if there is no title, then the notebook filename will be used
- if nbpublish.py is called on a folder, then the meta data from the first notebook will be used
- logo should be the path (absolute or relative) to a logo image file

To control the output of **contents tables**:

```json
{
"latex_doc": {
  "toc": true,
  "listfigures": true,
  "listtables": true,
  "listcode": true,
  }
}
```

To override the default **placement of figures and tables**:

```json
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
```

See [Positioning_images_and_tables](https://www.sharelatex.com/learn/Positioning_images_and_tables) for placement options.

### Cell Tags

To  **ignore any cell**:

```json
{
"latex_doc": {
	"ignore" : true
	}
}
```

To  **output a code block**:

```json
{
"latex_doc": {
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
```

all extra tags are optional:

- `format` can contain any keywords related to the latex [Listings](https://en.wikibooks.org/wiki/LaTeX/Source_Code_Listings) package (such as syntax highlighting colors)
- `asfloat` contitutes whether the code is wrapped in a codecell (float) environment or is inline.
- all other tags work the same as figure (below).

To  **output text produced by the code** (e.g. *via* the `print` command):

```json
{
"latex_doc": {
  "text": {
      "format": {
       "basicstyle": "\\small"
      },
    "asfloat": true,
    "caption": "",
    "label": "code:example_sym",
    "widefigure": false,
    "placement": "H"
    }
  }
}
```

all extra tags are optional:

- `format` can contain any keywords related to the latex [Listings](https://en.wikibooks.org/wiki/LaTeX/Source_Code_Listings) package (such as syntax highlighting colors). N.B. in place of `\` use `\\`.
- `asfloat` contitutes whether the code is wrapped in a codecell (float) environment or is inline.
- all other tags work the same as figure (below).


For **figures** (i.e. any graphics output by the code), enter in cell metadata:

```json
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
```

- `caption` and `label` are optional
- `placement` is optional and constitutes using a placement arguments for the figure (e.g. \begin{figure}[H]). See [Positioning_images_and_tables](https://www.sharelatex.com/learn/Positioning_images_and_tables).
- `widefigure` is optional and constitutes expanding the figure to the page width (i.e. \begin{figure*}) (placement arguments will then be ignored)

For  **tables** (e.g. those output by `pandas`), enter in cell metadata:

```json
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
```

- `caption` and `label` are optional
- `placement` is optional and constitutes using a placement arguments for the table (e.g. \begin{table}[H]). See [Positioning_images_and_tables](https://www.sharelatex.com/learn/Positioning_images_and_tables).
- `alternate` is optional and constitutes using alternating colors for the table rows (e.g. \rowcolors{2}{gray!25}{white}). See (https://tex.stackexchange.com/a/5365/107738)[https://tex.stackexchange.com/a/5365/107738].


For  **equations** (e.g. thos output by `sympy`), enter in cell metadata:

```json
{
  "latex_doc": {
	  "equation": {
	    "label": "eqn:elabel"
	  }
  }
}
```

- label is optional

### Captions in a Markdown cell

Especially for long captions, it would be prefered that they can be viewed and edited in a notebook Markdown cell, rather than hidden in the metadata. This can be achieved using the default ipypublish converters:

If a **markdown input** or **latex output** cell has the metadata tag:

```json
{
 "latex_doc": {
	"caption": "fig:example_mpl"
	}
}
```

Then, during the the postprocessor stage, this cell will be removed from the notebook object, and its text stored as a *resource*;

- the cell's text is the first paragraph of the markdown string, i.e. nothing after a newline (\n) 
- if there are multiple instance of the same cation name, then only the last instance will be stored

During the jinja templating, if a **figure, table or code** cell has a label matching any stored caption name, for example:

```json
{
"latex_doc": {
	"figure": {
	  "caption": "",
	  "label": "fig:example_mpl"
	}
  }
}
```

Then its caption will be overriden with the stored text. 

### Embedding Interactive HTML

Packages built on [IPywidgets](http://ipywidgets.readthedocs.io), 
like [PythreeJS](https://github.com/jovyan/pythreejs), 
[Pandas3JS](https://github.com/chrisjsewell/pandas3js) 
and the excellent [IPyvolume](https://ipyvolume.readthedocs.io/en/latest/), 
are making it increasingly easier to render complex, interactive html in the notebook. 
IPywidgets offers a [save notebook with widgets](http://ipywidgets.readthedocs.io/en/latest/embedding.html) feature, however, this can greatly increase the size of the notebook.


A better solution, recently offered, is to save a [html snippet](http://ipywidgets.readthedocs.io/en/latest/embedding.html#embeddable-html-snippet) 
of the current widget state to file. 
This file can be re-embedded into the notebook, at the conversion stage, 
using the `embed_html` tag, then treating it as any other output in the notebook.

```json
{
  "latex_doc": {
    "embed_html": {
      "filepath": "path/to/embed.html"
    },
    "figure": {
      "caption": "An example of embedded html"
    }
  }
}
```

A possible workflow is then to have a single notebook cell with a static image of the widget in the output, and a path to the embed html in the metadata so that a) if you export to latex/pdf, you get the static image or b) if you export to html/reveal slides, you get the html. 

An example of how this works is in the [Example.ipynb](example/notebooks/Example.pdf), and the 
[Example.html](https://chrisjsewell.github.io/ipypublish/Example.html#Embedded-HTML-6) and 
[Example.slides.html](https://chrisjsewell.github.io/ipypublish/Example.slides.html#/9) outputs. 

## Citations and Bibliography

Using Zotero's Firefox plugin and [Zotero Better Bibtex](https://github.com/retorquere/zotero-better-bibtex/releases/tag/1.6.100) for;

- automated .bib file updating 
- drag and drop cite keys \cite{kirkeminde_thermodynamic_2012}
- `latexmk -bibtex -pdf` (in nbpublish.py) handles creation of the bibliography
- \usepackage{doi} turns the DOI numbers into url links

    - in Zotero-Better-Bibtex I have the option set to only export DOI, if both DOI and URL are present.
	
Please note, at the time of writing, Better BibTeX does not support Zotero 5.0 ([issue#555](https://github.com/retorquere/zotero-better-bibtex/issues/555)). For now I have turned off auto-updates of Zotero, though this is probably not wise for long ([Zotero 5 Discussion](https://forums.zotero.org/discussion/comment/277434/#Comment_277434)).

Can use: 

```html
<cite data-cite="kirkeminde_thermodynamic_2012">(Kirkeminde, 2012)</cite> 
```

to make it look better in html, but not specifically available for drag and drop in Zotero 
	
## Live Slideshows

The **nbpresent** script handles serving [reveal.js](http://lab.hakim.se/reveal-js/#/) slides to a webbrowser. To see all options for this script:

	nbpresent -h
	
Note that, for offline use, simply download the latest version of reveal.js [here](https://github.com/hakimel/reveal.js/releases), rename the entire folder to reveal.js and place it in the same folder as the converted .slides.html file. The slides can also be save to PDF my appending `pdf-export` to the url (see [here](https://github.com/hakimel/reveal.js#pdf-export) for details).


Additionally, the [Reveal.js - Jupyter/IPython Slideshow Extension (RISE)](https://github.com/damianavila/RISE) notebook extension offers rendering as a Reveal.js-based slideshow, where you can execute code or show to the audience whatever you can show/do inside the notebook itself! Click on the image to see a demo:

[![RISE Demo](https://img.youtube.com/vi/sXyFa_r1nxA/0.jpg)](https://www.youtube.com/watch?v=sXyFa_r1nxA) 

## Dealing with external data

A goal for scientific publishing is automated reproducibility of analyses, which the Jupyter notebook excels at. But, more than that, it should be possible to efficiently reproduce the analysis with different data sets. This entails having **one point of access** to a data set within the notebook, rather than having copy-pasted data into variables, i.e. this:

```python
data = read_in_data('data_key')
variable1 = data.key1
variable2 = data.key2
...
```

rather than this:

```python
variable1 = 12345
variable2 = 'something'
...
```

The best-practice for accessing heirarchical data (in my opinion) is to use the JSON format (as long as the data isn't [relational](http://www.sarahmei.com/blog/2013/11/11/why-you-should-never-use-mongodb/)), because it is:

- applicable for any data structure
- lightweight and easy to read and edit
- has a simple read/write mapping to python objects (using [json](https://docs.python.org/3.6/library/json.html))
- widely used (especially in web technologies)

A good way to store multiple bits of JSON data is in a [mongoDB](https://docs.mongodb.com/manual/administration/install-community/) and accessing it via [pymongo](https://api.mongodb.com/python/current/). This will also make it easy to move all the data to a cloud server at a later time, if required.

    conda install pymongo

But, if the data is coming from files output from different simulation or experimental code, where the user has no control of the output format. Then writing JSON parsers may be the way to go, and this is where [jsonextended](https://github.com/chrisjsewell/jsonextended) comes in, which implements:

- a lightweight plugin system to define bespoke classes for parsing different file extensions and data types.
- a 'lazy loader' for treating an entire directory structure as a nested dictionary.

For example:

```python
from jsonextended import plugins, edict
plugins.load_plugins_dir('path/to/folder_of_parsers','parsers')
data = edict.LazyLoad('path/to/data')
variable1 = data.folder1.file1_json.key1
variable2 = data[['folder1','file1.json','key2']]
variable3 = data[['folder1','file2.csv','key1']]
variable4 = data[['folder2','subfolder1','file3.other','key1']]
...    
```

If you are dealing with numerical data arrays which are to large to be loaded directly in to memory, 
then the [h5py](http://docs.h5py.org/en/latest/index.html) interface to the [HDF5](http://hdfgroup.org/) binary data format,
allows for the manipultion of even multi-terabyte datasets stored on disk, as if they were real NumPy arrays. 
These files are also supported by [jsonextended](https://github.com/chrisjsewell/jsonextended) lazy loading.

## Miscellaneous

I also use the Firefox Split Pannel extension to view the {name}_viewpdf.html page and monitor changes to the pdf.

[bookbook](https://github.com/takluyver/bookbook) is another package with some conversion capabilities.

## Acknowledgements

I took strong influence from:

- [Julius Schulz](http://blog.juliusschulz.de/blog/ultimate-ipython-notebook)
- [Dan Mackinlay](https://livingthing.danmackinlay.name/jupyter.html)
- Notebook concatination was adapted from [nbconvert issue#253](https://github.com/jupyter/nbconvert/issues/253)


