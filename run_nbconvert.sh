#!/bin/bash

bib_path=""
logo_path=""
output_format="latex_ipypublish_main.py"
nconvert_path="nbconvert"
create_pdf=true
copy_images=false

usage="usage: run_nbconvert [-h -b -l -f —n -p] ipynb_path 
program to convert jupyter notebooks to tex and pdf format

where:
   ipynb_path = notebook file or directory
    -h  show this help text
    -b  path to bibliography
    -l  path to title page logo
    -f  output format file to use (default: ${output_format})
    -n  path to nbconvert folder (default: ${nconvert_path})
	-p  true/false create pdf (if converting to latex)  (default: ${create_pdf})
	-i  true/false copy image folder to output (if converting to latex) (default: ${copy_images})
"

OPTIND=1
while getopts ':hb:l:f:n:p:i:' option; do
  case "$option" in
    h) echo "$usage"
       return 0
       ;;
    b) bib_path=$OPTARG
       ;;
    l) logo_path=$OPTARG
       ;;
    f) output_format=$OPTARG
       ;;
    n) nconvert_path=$OPTARG
       ;;
    p) create_pdf=$OPTARG
      ;;
    i) copy_images=$OPTARG
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

if [ ! -e "${nconvert_path}/scripts/${output_format}" ]; then
	echo "ERROR: ${output_format} does not exist"
	exit
fi

rm -f "${nconvert_path}/${ipynb_name}".*
if [ -d "${nconvert_path}/${ipynb_name}_files" ]; then
	rm -rf "${nconvert_path}/${ipynb_name}_files"
fi

if [[ -d "$ipynb_path" ]]; then
	echo "Merging all notebooks in directory..."
	python "${nconvert_path}/scripts/nbmerge.py" "$ipynb_path" > "${nconvert_path}/${ipynb_name}.ipynb"
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

cp "scripts/${output_format}" "${output_format}"

jupyter nbconvert "${ipynb_name}.ipynb" --config "${output_format}"

rm -r "${output_format}"

if [ ! -e "${ipynb_name}.tex" ]; then
	if [ ! -e "${ipynb_name}.html" ]; then	
		echo "Error: no latex or html file created, check files in ${nconvert_path} for issues"
		cd -
		exit
	else
		cd -
		if [ ! -d "converted" ]; then
			mkdir converted
		fi
		cp "${nconvert_path}/${ipynb_name}.html"  "converted/${ipynb_name}.html"
		echo "Finished: output copied to: converted/${ipynb_name}.html"
				
	fi
else

	if [ ! -d "converted" ]; then
		mkdir converted
	fi

	if [ "${create_pdf}" = true ] ; then
		latexmk -bibtex -pdf "${ipynb_name}.tex" | tee latex_to_pdf.log
		cd -
		cp "${nconvert_path}/latex_to_pdf.log"  "converted/${ipynb_name}.latex_to_pdf.log"
		sed 's/{name_of_pdf_here}/'"${ipynb_name}.pdf"'/' < "${nconvert_path}/scripts/view_pdf.html" > "converted/${ipynb_name}_viewpdf.html"
		cp "${nconvert_path}/${ipynb_name}.pdf"  "converted/${ipynb_name}.pdf"
	else
		cd -
    fi
	
	cp "${nconvert_path}/${ipynb_name}.tex"  "converted/${ipynb_name}.tex"
	if [ "${copy_images}" = true ] ; then
		rm -rf "converted/${ipynb_name}_files"
		cp -r "${nconvert_path}/${ipynb_name}_files" converted
	fi
	echo "Finished: output copied to: converted/${ipynb_name}.*"

	rm -rf "${nconvert_path}/${ipynb_name}_files"	
fi

rm -f "${nconvert_path}/${ipynb_name}".*
if [[ -e "${bib_path}" ]]; then
	rm -f  "${nconvert_path}/bibliography.bib"
fi
if [[ -e "${logo_path}" ]]; then
	rm -f  "${nconvert_path}/${logo_path##*/}"
fi
