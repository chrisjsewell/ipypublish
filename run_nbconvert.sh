#!/bin/bash

ipynb_path=$1
bib_path="bibliography/pyatomica.bib"

latex_format="hide_input_output"

cp "${ipynb_path}" nbconvert/notebook.ipynb
cp "${bib_path}" nbconvert/bibliography.bib

cd nbconvert

jupyter nbconvert notebook.ipynb --config "latex_${latex_format}.py"

# TODO check notebook.tex exists else exit

# by default captions are set to not have captions
sed -i.bak '/DeclareCaptionLabelFormat/d' notebook.tex
sed -i.bak '/captionsetup{labelformat=nolabel}/d' notebook.tex
rm -f notebook.tex.bak

latexmk -bibtex -pdf notebook.tex
./cleantex.sh notebook
cd ..

ipynb_file=${ipynb_path##*/}
ipynb_name=${ipynb_file%.*}
cp nbconvert/notebook.pdf  "${ipynb_name}.pdf"
cp nbconvert/notebook.tex  "${ipynb_name}.tex"

rm -f nbconvert/notebook.pdf
rm -f nbconvert/notebook.tex
rm -f nbconvert/bibliography.bib
rm -f nbconvert/notebook.ipynb

