# ipypublish
A workflow for creating/editing publication ready scientific reports from one or more Jupyter Notebooks, without leaving the browser!

![WorkFlow Example](/example_workflow.gif)

See ![notebooks/Example.ipynb](converted/Example.pdf) and ![converted/Example.pdf](converted/Example.pdf) for an example of the potential input/output.

## Workflow

1. Create a notebook with some content!
2. optionaly create a .bib file and logo image
3. Adjust the notebook and cell metadata. 
4. Run the run_nbconvert.sh script for either the specific notebook, or a folder containing multiple notebooks. 
5. A converted folder will be created, into which final .tex .pdf and _viewpdf.html files will be output, named by the notebook or folder input

The default latex template (latex_hide_input_output.tplx) outputs all raw/markdown cells (unless tagged latex_ignore), and then only output cells with latex_figure, latex_table or latex_equation meta tags (see Metadata Tags).

## Setup

Using [Conda](https://conda.io/docs/) is recommended:

	conda create --name ipyreport -c conda-forge jupyter

For helpful tools in the notebook (like toc sidebar):

	conda install --name ipyreport jupyter_contrib_nbextensions
	
For a more extensive setup of useful packages:

	conda create --name ipyreport -c conda-forge -c matsci --file conda_packages.txt

## run_nbconvert script

To see all options for this script:

	./run_nbconvert.sh -h

For example, to convert the Example.ipynb notebook:

	./run_nbconvert.sh -b bibliographies/example.bib -l logos/logo_example.png notebooks/Example.ipynb

If a folder is input, then the .ipynb files it contains are processed and combined in 'natural' sorted order, i.e. 2_name.ipynb before 10_name.ipynb

The current `nbconvert --to pdf` does not correctly resolve references and citations (since it copies the files to a temporary directory). Therefore nbconvert is only used for the initial `nbconvert --to latex` phase, followed by using `latexmk` to create the pdf and correctly resolve everything.
 
## Metadata Tags

For titlepage, enter in notebook metadata:

  "latex_metadata": {
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
    "logo": "logo_example"
  },
	
- all keys are optional
- if there is no title, then the notebook filename will be used
- if run_nbconvert.sh is called on a folder, then the meta data from the first notebook will be used
- logo should be the name (without extension) of the logo, then use e.g. `run_nbconvert.sh -l logos/logo_example.png Example.ipynb`

To ignore a markdown cell:

	"latex_ignore" : true

For figures, enter in cell metadata:

	  "latex_figure": {
	    "caption": "Figure caption.",
	    "label": "fig:flabel",
	    "placement": "H"
	    "widefigure": false
	  }

- `placement` is optional and constitutes using a placement arguments for the figure (e.g. \begin{figure}[H]). See https://www.sharelatex.com/learn/Positioning_images_and_tables.
- `widefigure` is optional and constitutes expanding the figure to the page width (i.e. \begin{figure*}) (placement arguments will then be ignored)

For tables, enter in cell metadata:

	  "latex_table": {
	    "caption": "Table caption.",
	    "label": "tbl:tlabel"
	    "placement": "H"
        "alternate": "gray!20"
	  }

- `placement` is optional and constitutes using a placement arguments for the table (e.g. \begin{table}[H]). See https://www.sharelatex.com/learn/Positioning_images_and_tables.
- `alternate` is optional and constitutes using alternating colors for the table rows (e.g. \rowcolors{2}{gray!25}{white}). See https://tex.stackexchange.com/a/5365/107738.


For equations, enter in cell metadata:

	  "latex_equation": {
	    "label": "eqn:elabel"
	  }

label is optional

## Citations and Bibliography

Using Zotero's Firefox plugin and https://github.com/retorquere/zotero-better-bibtex/releases/tag/1.6.100 for;

- automated .bib file updating 
- drag and drop cite keys \cite{kirkeminde_thermodynamic_2012}
- `latexmk -bibtex -pdf` (in run_nbconvert.sh) handles creation of the bibliography
- \usepackage{doi} turns the DOI numbers into url links

    - in Zotero-Better-Bibtex I have the option set to only export DOI, if both DOI and URL are present.

Can use: 

	<cite data-cite="kirkeminde_thermodynamic_2012">(Kirkeminde, 2012)</cite> 
	
to make it look better in html, but not specifically available for drag and drop in Zotero 

## Notebook code for improved latex/pdf output

	%matplotlib inline
	%config InlineBackend.figure_format = 'svg'
	import matplotlib as mpl
	mpl.rcParams['figure.figsize'] = (5.0, 2.5)
	import matplotlib.pyplot as plt

	import pandas as pd
	import numpy as np
	pd.set_option('display.latex.repr',True)
	pd.set_option('display.latex.longtable',False)
	pd.set_option('display.latex.escape',False)
	import sympy
	sympy.init_printing(use_latex=True)

	from IPython.display import Image, Latex

	from PIL import Image as PImage
	def read_images(paths):
	    return [PImage.open(i).convert("RGBA") for i in paths]
	def images_hconcat(images, width=700,height=700, 
	                   gap=0,aspaths=True):
		""" concatenate multiple images horizontally """
	    images = read_images(images) if aspaths else images
	    widths, heights = zip(*(i.size for i in images))
	    total_width = sum(widths) + gap*len(images)
	    max_height = max(heights)
	    new_im = PImage.new('RGBA', (total_width, max_height))
	    x_offset = 0
	    for im in images:
	        new_im.paste(im, (x_offset,0),mask=im)
	        x_offset += im.size[0] + gap
	    new_im.thumbnail((width,height), PImage.ANTIALIAS)
	    return new_im
	def images_vconcat(images, width=700,height=700, 
	                   gap=0, aspaths=True):
		""" concatenate multiple images vertically """
	    images = read_images(images) if aspaths else images
	    widths, heights = zip(*(i.size for i in images))
	    max_width = max(widths)
	    total_height = sum(heights) + gap*len(images)
	    new_im = PImage.new('RGBA', (max_width, total_height))
	    y_offset = 0
	    for im in images:
	        new_im.paste(im, (0,y_offset),mask=im)
	        y_offset += im.size[1] + gap
	    new_im.thumbnail((width,height), PImage.ANTIALIAS)
	    return new_im
	def images_gridconcat(pathslist,width=700,height=700,
	                     aspaths=True,hgap=0,vgap=0):
		""" concatenate multiple images in a grid 
		
		pathslist : list of lists
		"""
	    himages = [images_hconcat(paths,gap=hgap,aspaths=aspaths) for paths in pathslist]
	    new_im = images_vconcat(himages,gap=vgap,aspaths=False)
	    new_im.thumbnail((width,height), PImage.ANTIALIAS)
	    return new_im
	
## Miscellaneous

I also use the Firefox Split Pannel extension to view the {name}_viewpdf.html page and monitor changes to the pdf.

## Acknowledgements

I took strong influence from:

- http://blog.juliusschulz.de/blog/ultimate-ipython-notebook#cite2c
- https://livingthing.danmackinlay.name/jupyter.html
- Notebook concatination adapted from https://github.com/jupyter/nbconvert/issues/253
