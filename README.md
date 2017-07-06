# pyatomica
A package for analysis of atomic/electonic level data

## Metadata

For titlepage, enter in notebook metadata:

	"latex_metadata": {
	  "title": "Article Name",
	  "subtitle": 
	},
	
all keys are optional

To ignore a markdown cell:

	"latex_ignore" : true

For figures, enter in cell metadata:

	  "latex_figure": {
	    "caption": "Figure caption.",
	    "label": "fig:flabel",
	    "widefigure": false
	  }

For tables, enter in cell metadata:

	  "latex_table": {
	    "caption": "Table caption.",
	    "label": "tbl:tlabel"
	  }

For tables, enter in cell metadata:

	  "latex_equation": {
	    "label": "eqn:elabel"
	  }

label is optional
NB: two dollar signs are required, i.e. 

	\$$equation\$$

## Citations

Using https://github.com/retorquere/zotero-better-bibtex/releases/tag/1.6.100 for drag and drop cite keys \cite{kirkeminde_thermodynamic_2012}

Can use: 

	<cite data-cite="kirkeminde_thermodynamic_2012">(Kirkeminde, 2012)</cite> 
	
to make it look better in html, but not specifically available for drag and drop in Zotero 

