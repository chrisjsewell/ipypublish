#!/bin/bash

bib_path=""
logo_path=""
latex_format="latex_hide_input_output.py"
nconvert_path="nbconvert"

# bib_path=${2:-"bibliographies/example.bib"}
# logo_path=${3:-"logos/logo_example.png"}

usage="usage: run_nbconvert [-h -b -l -f —n] ipynb_path 
program to convert jupyter notebooks to tex and pdf format

where:
   ipynb_path = notebook file or directory
    -h  show this help text
    -b  path to bibliography
    -l  path to title page logo
    -f  latex format file to use (default: ${latex_format})
    -n  path to nbconvert folder (default: ${nconvert_path})
"

OPTIND=1
while getopts ':hb:l:f:n:' option; do
  case "$option" in
    h) echo "$usage"
       return 0
       ;;
    b) bib_path=$OPTARG
       ;;
    l) logo_path=$OPTARG
       ;;
    f) latex_format=$OPTARG
       ;;
    n) nconvert_path=$OPTARG
       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       return 1
       ;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       echo "$usage" >&2
       return 1
       ;;
  esac
done
shift "$((OPTIND - 1))"

ipynb_path=$1

if [ ! -e "$ipynb_path" ]; then
	echo "ERROR: $ipynb_path does not exist"
	exit
fi
ipynb_file=${ipynb_path##*/}
ipynb_name=${ipynb_file%.*}

if [ ! -e "$bib_path" ]; then
	echo "ERROR: $bib_path does not exist"
	exit
fi

if [[ -d "$ipynb_path" ]]; then
	echo "Merging all notebooks in directory..."
	python "${nconvert_path}/nbmerge.py" "$ipynb_path" > "${nconvert_path}/${ipynb_name}.ipynb"
else
	cp "${ipynb_path}" "${nconvert_path}/${ipynb_name}.ipynb"
fi

if [[ -e "${bib_path}" ]]; then
	cp "${bib_path}" "${nconvert_path}/bibliography.bib"
fi
if [[ -e "${logo_path}" ]]; then
	cp "${logo_path}" "${nconvert_path}/${logo_path##*/}"
fi

cd "${nconvert_path}"

jupyter nbconvert "${ipynb_name}.ipynb" --config "${latex_format}"

if [ ! -e "${ipynb_name}.tex" ]; then
	echo "ERROR: latex file not created"
	cd ..
	exit
fi

##post-processing hacks
##---------------------
# by default captions are set to not have labels, need to remove this
sed -i.bak '/DeclareCaptionLabelFormat/d' "${ipynb_name}.tex"
sed -i.bak '/captionsetup{labelformat=nolabel}/d' "${ipynb_name}.tex"
# clereref must be loaded after anything that changes the referencing system
sed -i.bak 's=\\begin{document}=\\usepackage{cleveref}&=g' "${ipynb_name}.tex"
sed -i.bak 's=\\begin{document}=\\creflabelformat{equation}{#2#1#3}&=g' "${ipynb_name}.tex"
rm -f "${ipynb_name}.tex.bak"

latexmk -bibtex -pdf "${ipynb_name}.tex"
./cleantex.sh "${ipynb_name}"
cd -

if [ ! -d "converted" ]; then
	mkdir converted
fi
cp "${nconvert_path}/${ipynb_name}.pdf"  "converted/${ipynb_name}.pdf"
cp "${nconvert_path}/${ipynb_name}.pdf"  "converted/${ipynb_name}.tex"
sed 's/{name_of_pdf_here}/'"${ipynb_name}.pdf"'/' < "${nconvert_path}/view_pdf.html" > "converted/${ipynb_name}_viewpdf.html"

rm -f "${nconvert_path}/${ipynb_name}.pdf"
rm -f "${nconvert_path}/${ipynb_name}.tex"
rm -f "${nconvert_path}/${ipynb_name}.ipynb"

if [[ -e "${nconvert_path}/bibliography.bib" ]]; then
	rm -f "${nconvert_path}/bibliography.bib"
fi
if [[ -e "${nconvert_path}/${logo_path##*/}" ]]; then
	rm -f "${nconvert_path}/${logo_path##*/}"
fi

