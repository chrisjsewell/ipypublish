tplx_dict = { 
'meta_docstring':'with the main ipypublish article setup',

'document_docclass':r"""
	\documentclass[10pt,parskip=half,
	toc=sectionentrywithdots,
	bibliography=totocnumbered,
	captions=tableheading,numbers=noendperiod]{scrartcl}

""",

'document_packages':r"""
	\usepackage[a4paper,total={6in, 9in}]{geometry}
	\usepackage{microtype} % improves the spacing between words and letters
	\usepackage[section]{placeins} % placement of figures
	% Places the float at precisely the location in the LaTeX code (with H)
	\usepackage{float}
	\usepackage[colorinlistoftodos,obeyFinal]{todonotes} % to mark to-dos
	% number figures, tables and equations by section
	\usepackage{chngcntr}
	% header/footer
	\usepackage[footsepline=0.25pt]{scrlayer-scrpage}

""",

'document_definitions':r"""
    % Colors for the hyperref package
    \definecolor{urlcolor}{rgb}{0,.145,.698}
    \definecolor{linkcolor}{rgb}{.71,0.21,0.01}
    \definecolor{citecolor}{rgb}{.12,.54,.11}

""",

'document_commands':r"""
	% ensure new section starts on new page
	\addtokomafont{section}{\clearpage}

    % Prevent overflowing lines due to hard-to-break entities
    \sloppy 

    % Setup hyperref package
    \hypersetup{
      breaklinks=true,  % so long urls are correctly broken across lines
      colorlinks=true,
      urlcolor=urlcolor,
      linkcolor=linkcolor,
      citecolor=citecolor,
      }

	% number figures, tables and equations by section
	\usepackage{chngcntr}
	\counterwithout{figure}{section}
	\counterwithout{table}{section}
	\counterwithout{equation}{section}
	\makeatletter
	\@addtoreset{table}{section}
	\@addtoreset{figure}{section}
	\@addtoreset{equation}{section}
	\makeatother
	\renewcommand\thetable{\thesection.\arabic{table}}
	\renewcommand\thefigure{\thesection.\arabic{figure}}
	\renewcommand\theequation{\thesection.\arabic{equation}}

    % align captions to left (indented)
	\captionsetup{justification=raggedright,
	singlelinecheck=false,format=hang,labelfont={it,bf}} 

	% shift footer down so space between separation line
	\ModifyLayer[addvoffset=.6ex]{scrheadings.foot.odd}
	\ModifyLayer[addvoffset=.6ex]{scrheadings.foot.even}
	\ModifyLayer[addvoffset=.6ex]{scrheadings.foot.oneside}
	\ModifyLayer[addvoffset=.6ex]{plain.scrheadings.foot.odd}
	\ModifyLayer[addvoffset=.6ex]{plain.scrheadings.foot.even}
	\ModifyLayer[addvoffset=.6ex]{plain.scrheadings.foot.oneside}
	\pagestyle{scrheadings}
	\clearscrheadfoot{}
	\ifoot{\leftmark}
	\renewcommand{\sectionmark}[1]{\markleft{\thesection\ #1}}
	\ofoot{\pagemark}
	\cfoot{}

""",

'document_header_end':r"""
% clereref must be loaded after anything that changes the referencing system
\usepackage{cleveref}
\creflabelformat{equation}{#2#1#3}
"""

}