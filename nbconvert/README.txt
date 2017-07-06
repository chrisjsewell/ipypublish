use either:

jupyter nbconvert notebook.ipynb --to html --template html_<options>.tpl
or
jupyter nbconvert notebook.ipynb --config pdf_<options>.py 

see: http://blog.juliusschulz.de/blog/ultimate-ipython-notebook#cite2c for some interesting ways to caption figures, etc
     https://livingthing.danmackinlay.name/jupyter.html
	 
Citations
---------
<cite data-cite="cite_key">text to show</cite>

Metadata
--------

For titlepage, enter in notebook metadata:

"latex_metadata": {
  "title": "Article Name",
  "author": "Chris J Sewell"
},

For figures, enter in cell metadata:

  "latex_figure": {
    "caption": "Figure caption.",
    "label": "fig:flabel",
    "widefigure": false
  }



	 
	 