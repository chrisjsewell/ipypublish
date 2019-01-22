# Releases

## v0.6.8 - version bump to initiate Zenodo 

 

## v0.6.7 - Added support for raw cells 

Raw output is now included in the latex (if raw format is latex), and html (if raw format is html) 

## v0.6.5 - Minor Update 

 

## v0.6.4 - Encoding Bug Fixes for Python < 3.6 

and addition of documentation 

## v0.6.3 - better support for latex math environments 

 

## v0.6.2 - Améliorations! 

- added language translation 
- added width/height options for latex figures 
- changed embedded html to be iframes, with lazy loading for reveal 
slides 
- added titles and author for html and slides 
- bibtexparser uses "link" rather than "url" key (fixed) 
- fixed regex for headers (one or more # not zero or more) 
- allow codecells with no outputs 
- added ansi colors for latex listings 
- added adjust box for resizing tables too wide to fit in page width 
 

## v0.6.1 - added output level metadata 

see https://github.com/chrisjsewell/ipypublish#metadata-tags  

## v0.6.0 - changed top-level meta tag from latex_doc -> ipub 

To reflect that it also applys to html/slides output 
 
also: 
- improved control of slide output 
- changed from using utf8x -> xelatex, for handling font encoding 
- added mkdown output tag 

## v0.5.3 - Small bug fix for html caption prefixing 

- moved html caption prefixing to LatexCaption, so that captions from other cells are prefixed 
 
 
 

## v0.5.2 - Slide autonumbering and captions from code output 

 

## v0.5.1 - Improvements to Slide Output and Smart Slide Creation 

slide rows/columns partitioned by markdown headers 
 
also improved latex listings default options for text & stream data 

## v0.5.0 - Default Conversion Plugins & Enhancements to HTML/Slides Conversion 

- added auto numbering and correct reference hyperlinks for figures/tables/equations/code in html & slides 
- added text meta-tag, default meta-tag post processor, and additional converters based on it 
- added embeddable html 
 
 
 
 
 
 
 
 

## v0.4.1 - added universal bdist flag 

 

## v0.4.0 - Introducing nbpresent: for reveal.js slideshow creation and serving 

a lot of refactoring of html template creation 
improvement of command line argument processing 
introduction of preprocessors  
general awesomeness 

## v0.3.0 - First full, tested pypi release! 

 

## v0.2 - New Latex Metadata convention 

Now all under "latex_doc" key with no "latex_" prefix , e.g. 
 
```json 
{ 
"latex_doc" : { 
    "ignore": true 
    } 
} 
``` 
 
instead of: 
 
```json 
{"latex_ignore": true} 
``` 

## v0.1 - An initial release 

before changing latex meta tag convention 

