# ipypublish
A workflow for creating/editing publication ready scientific reports from one or more Jupyter Notebooks, without leaving the browser!

![WorkFlow Example](/example_workflow.gif)

See ![notebooks/Example.ipynb](converted/Example.pdf) and ![converted/Example.pdf](converted/Example.pdf) for an example of the potential input/output.

- [Workflow](#worklow)
- [Setting up the environment](#setting-up-the-environment)
- [Setting up a Notebook ](#setting-up-a-notebook)
- [Running run_nbconvert script](#running-run_nbconvert-script)
- [Metadata Tags](#metadata-tags)
- [Citations and Bibliography](#citations-and-bibliography)
- [Miscellaneous](#miscellaneous)
- [Acknowledgements](#acknowledgements)

## Workflow

1. Create a notebook with some content!
2. optionaly create a .bib file and logo image
3. Adjust the notebook and cell metadata. 
4. Run the run_nbconvert.sh script for either the specific notebook, or a folder containing multiple notebooks. 
5. A converted folder will be created, into which final .tex .pdf and _viewpdf.html files will be output, named by the notebook or folder input

The default latex template (latex_hide_input_output.tplx) outputs all raw/markdown cells (unless tagged latex_ignore), and then only output cells with latex_figure, latex_table or latex_equation meta tags (see Metadata Tags).

## Setting up the environment

Using [Conda](https://conda.io/docs/) is recommended:

	conda create --name ipyreport -c conda-forge jupyter

For helpful tools in the notebook (like toc sidebar):

	conda install --name ipyreport jupyter_contrib_nbextensions
	
For a more extensive setup of useful packages:

	conda create --name ipyreport -c conda-forge -c matsci --file conda_packages.txt

## Setting up a Notebook 

For improved latex/pdf output, ![notebooks/ipynb_latex_setup.py](notebooks/ipynb_latex_setup.py) contains import and setup code for the notebook and a number of common packages and functions, including:

- numpy, matplotlib, pandas, sympy, ...
- `images_hconcat`, `images_vconcat` and `images_gridconcat` functions, which use the PIL/Pillow package to create a single image from multiple images (with specified arrangement)

To use this script, in the first cell of a notebook, insert:

	from ipynb_latex_setup import *
	
It is recommended that you also set this cell as an initialisation cell (i.e. have `"init_cell": true` in the metadata)

## Running run_nbconvert script

To see all options for this script:

	./run_nbconvert.sh -h

For example, to convert the Example.ipynb notebook:

	./run_nbconvert.sh -b bibliographies/example.bib -l logos/logo_example.png notebooks/Example.ipynb

If a folder is input, then the .ipynb files it contains are processed and combined in 'natural' sorted order, i.e. 2_name.ipynb before 10_name.ipynb

The current `nbconvert --to pdf` does not correctly resolve references and citations (since it copies the files to a temporary directory). Therefore nbconvert is only used for the initial `nbconvert --to latex` phase, followed by using `latexmk` to create the pdf and correctly resolve everything.
 
## Metadata Tags

For **titlepage**, enter in notebook metadata:

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

To  **ignore a markdown cell**:

	"latex_ignore" : true

For  **figures**, enter in cell metadata:

	  "latex_figure": {
	    "caption": "Figure caption.",
	    "label": "fig:flabel",
	    "placement": "H"
	    "widefigure": false
	  }

- `placement` is optional and constitutes using a placement arguments for the figure (e.g. \begin{figure}[H]). See https://www.sharelatex.com/learn/Positioning_images_and_tables.
- `widefigure` is optional and constitutes expanding the figure to the page width (i.e. \begin{figure*}) (placement arguments will then be ignored)

For  **tables**, enter in cell metadata:

	  "latex_table": {
	    "caption": "Table caption.",
	    "label": "tbl:tlabel"
	    "placement": "H"
        "alternate": "gray!20"
	  }

- `placement` is optional and constitutes using a placement arguments for the table (e.g. \begin{table}[H]). See https://www.sharelatex.com/learn/Positioning_images_and_tables.
- `alternate` is optional and constitutes using alternating colors for the table rows (e.g. \rowcolors{2}{gray!25}{white}). See https://tex.stackexchange.com/a/5365/107738.


For  **equations**, enter in cell metadata:

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
	
Please note, at the time of writing, Better BibTeX does not support Zotero 5.0 ([issue#555](https://github.com/retorquere/zotero-better-bibtex/issues/555)). For now I have turned off auto-updates of Zotero, though this is probably not wise for long ([Zotero 5 Discussion](https://forums.zotero.org/discussion/comment/277434/#Comment_277434)).

Can use: 

	<cite data-cite="kirkeminde_thermodynamic_2012">(Kirkeminde, 2012)</cite> 
	
to make it look better in html, but not specifically available for drag and drop in Zotero 
	
## Miscellaneous

I also use the Firefox Split Pannel extension to view the {name}_viewpdf.html page and monitor changes to the pdf.

## Acknowledgements

I took strong influence from:

- http://blog.juliusschulz.de/blog/ultimate-ipython-notebook#cite2c
- https://livingthing.danmackinlay.name/jupyter.html
- Notebook concatination adapted from https://github.com/jupyter/nbconvert/issues/253
