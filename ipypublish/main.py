#!/usr/bin/env python
import os, sys
import time
import re
import tempfile
import base64
import logging
import shutil
import subprocess
from subprocess import Popen, PIPE, STDOUT

# python 3 to 2 compatibility
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
try:
    basestring
except NameError:
    basestring = str
try:
    from shutil import which as exe_exists
except ImportError:
    from distutils.spawn import find_executable as exe_exists
        
from ipypublish import scripts
from ipypublish.scripts.nbmerge import merge_notebooks
from ipypublish.scripts.nbexport import export_notebook

VIEW_PDF = r"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"  
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>
    <meta http-equiv="content-type" content="text/html; charset=windows-1252">
    <title>View PDF</title>
	
    <script type="text/javascript">
 	   var filepath = "{pdf_name}";
       var timer = null;

       function refresh(){{
          var d = document.getElementById("pdf"); // gets pdf-div
          d.innerHTML = '<iframe style="position: absolute; height: 100%; border: none" id="ipdf" src='+window.filepath+'  width="100%"></iframe>';
       }}

       function autoRefresh(){{
          timer = setTimeout("autoRefresh()", 20000);
          refresh();
       }}

       function manualRefresh(){{
          clearTimeout(timer); 
          refresh();   
       }}
	   function check_pdf() {{
	     var newfile = document.f.userFile.value;
	     ext = newfile.substring(newfile.length-3,newfile.length);
	     ext = ext.toLowerCase();
	     if(ext != 'pdf') {{
	       alert('You selected a .'+ext+
	             ' file; please select a .pdf file instead!'+filepath);
	       return false; }}
	     else
			 alert(newfile);
		     window.filepath = newfile;
			 alert(filepath);
			 refresh();
	       return true; }}
    </script>

</head>
<body>
	<!-- <form name=f onsubmit="return check_pdf();"
	    action='' method='POST' enctype='multipart/form-data'>
	    <input type='submit' name='upload_btn' value='upload'>
		<input type='file' name='userFile' accept="application/pdf">
	</form> -->
	<button onclick="manualRefresh()">manual refresh</button>
   <button onclick="autoRefresh()">auto refresh</button>
   <div id="pdf"></div>
</body> 
<script type="text/javascript">refresh();</script>
</html>
"""

class change_dir:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def resolve_path(fpath, filepath):
    """resolve a relative path, w.r.t. another filepath """
    if not os.path.isabs(fpath):
        fpath = os.path.join(os.path.dirname(str(filepath)),fpath)
        fpath = os.path.abspath(fpath)
    return fpath
                
def publish(ipynb_path,
            outformat='latex_ipypublish_main',
            outpath=None, dump_files=False,
            ignore_prefix='_',
            create_pdf=False, pdf_in_temp=False, pdf_debug=False,
            loglevel='INFO'):
    """ convert one or more Jupyter notebooks to a published format

    paths can be string of an existing file or folder,
    or a pathlib.Path like object
              
    Parameters
    ----------
    ipynb_path
        notebook file or directory
    outformat: str
        output format to use
    outpath : path_like
        path to output converted files
    dump_files: bool
        whether to write files from nbconvert (containing images, etc) to outpath
    ignore_prefix: str
        ignore ipynb files with this prefix                
    create_pdf: bool
        whether to convert to pdf (if converting to latex)
    pdf_in_temp: bool
        whether to run pdf conversion in a temporary folder
    pdf_debug: bool
        if True, run latexmk in interactive mode
    loglevel: str
        the logging level
              
    Examples
    --------
              
    
    """
    ipynb_name = os.path.basename(ipynb_path.split('.')[0])
    files_folder = ipynb_name+'_files'

    outdir = os.path.join(os.getcwd(),'converted') if outpath is None else outpath 
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    slogger = logging.StreamHandler(sys.stdout)
    slogger.setLevel(getattr(logging,loglevel))
    formatter = logging.Formatter('%(levelname)s:%(message)s')
    slogger.setFormatter(formatter)
    root.addHandler(slogger)
    flogger = logging.FileHandler(os.path.join(outdir,ipynb_name+'.nbpub.log'), 'w')
    flogger.setLevel(getattr(logging,loglevel))
    root.addHandler(flogger)
    
    logging.info('started ipypublish at {0}'.format(time.strftime("%c")))
    logging.info('logging to: {}'.format(os.path.join(outdir,ipynb_name+'.nbpub.log')))    
    logging.info('running for ipynb(s) at: {0}'.format(ipynb_path))
    logging.info('with conversion: {0}'.format(outformat))
    
    final_nb, meta_path = merge_notebooks(ipynb_path,
                        ignore_prefix=ignore_prefix)
    logging.debug('notebooks meta path: {}'.format(meta_path))
    otherfiles=[]
    if hasattr(final_nb.metadata, 'latex_doc'):
        logging.info('resolving file paths in metadata.latex_doc')
        
        
        if hasattr(final_nb.metadata.latex_doc, 'files'):            
            for fpath in final_nb.metadata.latex_doc.files:
                fpath = resolve_path(fpath, meta_path)
                if not os.path.exists(fpath):
                    logging.warning('file in metadata does not exist'
                                    ': {}'.format(fpath))
                    continue
                otherfiles.append(fpath)
        
        # TODO do this individually for now, but should come up with more consistent method
        if hasattr(final_nb.metadata.latex_doc, 'bibliography'):                    
            bib = final_nb.metadata.latex_doc.bibliography
            bib = resolve_path(bib, meta_path)
            if not os.path.exists(bib):
                logging.warning('bib in metadata does not exist'
                                ': {}'.format(bib))
            else:
                otherfiles.append(bib)
            bib = os.path.join(files_folder,bib)
            final_nb.metadata.latex_doc.bibliography = bib
        if hasattr(final_nb.metadata.latex_doc, 'titlepage'):
            if hasattr(final_nb.metadata.latex_doc.titlepage, 'logo'):
                logo = final_nb.metadata.latex_doc.titlepage.logo
                logo = resolve_path(logo, meta_path)
                if not os.path.exists(logo):
                    logging.warning('logo in metadata does not exist'
                                    ': {}'.format(logo))
                else:
                    otherfiles.append(logo)
                logo = os.path.join(files_folder,logo)
                final_nb.metadata.latex_doc.titlepage.logo = logo

    logging.info('running nbconvert')
    try:
        outplugin = getattr(scripts, outformat)
    except AttributeError as err:
        raise ValueError('the outformat does not exist: {}'.format(outformat))
        
    oformat = outplugin.oformat
    otemplate = outplugin.template
    oconfig = outplugin.config
    oconfig['ExtractOutputPreprocessor.output_filename_template'] = files_folder+'/{unique_key}_{cell_index}_{index}{extension}'
    
    (body, resources), exe = export_notebook(final_nb, oformat,oconfig,otemplate)
    
    # remove reduce multiple blank lines to single
    body = re.sub(r'\n\s*\n', '\n\n', body)

    logging.info('outputting files to: {}'.format(outdir))    
    # output main file
    outpath = os.path.join(outdir,ipynb_name+exe)
    with open(outpath, "w") as fh:
        fh.write(body)

    # only output files that are in the document
    if resources['outputs']:
        outfiles = [path for path in resources['outputs'].keys() if path in body]
    else:
        outfiles = []
    if dump_files:
        outfilespath = os.path.join(outdir,files_folder)
        if not os.path.exists(outfilespath):
            os.mkdir(outfilespath)        
        for outname in outfiles:
            with open(os.path.join(outdir, outname), "wb") as fh:
                fh.write(resources['outputs'][outname])
        for othername in otherfiles:
            shutil.copyfile(othername, 
                os.path.join(outfilespath,os.path.basename(othername)))
     
    if create_pdf and oformat.lower()=='latex':
        logging.info('running pdf conversion')   
        
        if not exe_exists('latexmk'):
            logging.error('pdf conversion failed: requires the latexmk executable to run. See http://mg.readthedocs.io/latexmk.html#installation')
            raise RuntimeError('pdf conversion failed: requires the latexmk executable to run. See http://mg.readthedocs.io/latexmk.html#installation')
         
        if pdf_in_temp: 
            temp_folder = tempfile.mkdtemp()
        else:
            temp_folder = outdir
        try:
            outpath = os.path.join(temp_folder,ipynb_name+exporter.file_extension)
            outfilespath = os.path.join(temp_folder,files_folder)
            if pdf_in_temp: 
                with open(outpath, "w") as fh:
                    fh.write(body)
                    os.mkdir(os.path.join(outfilespath))
                for outname in outfiles:
                    with open(os.path.join(temp_folder, outname), "wb") as fh:
                        fh.write(resources['outputs'][outname])
                    
                for othername in otherfiles:
                    shutil.copyfile(othername, 
                        os.path.join(outfilespath,os.path.basename(othername)))
         
            with change_dir(temp_folder):
                latexmk = ['latexmk','-bibtex','-pdf']
                latexmk += [] if pdf_debug else ["--interaction=batchmode"]
                logging.info('running: '+' '.join(latexmk+['outpath']))
                latexmk += [outpath]

                def log_latexmk_output(pipe):
                    for line in iter(pipe.readline, b''):
                        logging.info('latexmk: {}'.format(line.decode("utf-8").strip()))
                process = Popen(latexmk, stdout=PIPE, stderr=STDOUT)
                with process.stdout:
                    log_latexmk_output(process.stdout)
                exitcode = process.wait() # 0 means success

                if exitcode == 0:
                    if pdf_in_temp: 
                        shutil.copyfile(ipynb_name+'.pdf',
                            os.path.join(outdir,ipynb_name+'.pdf'))
                    view_pdf = VIEW_PDF.format(pdf_name=ipynb_name+'.pdf')
                    with open(os.path.join(outdir,ipynb_name+'.view_pdf.html'),'w') as f:
                        f.write(view_pdf)
                    logging.info('pdf conversion complete')
                else:
                    logging.error('pdf conversion failed: '
                                  'Try running with pdf_debug=True')
           
        except Exception as err:
            logging.error('error in pdf conversion: {}'.format(err))
        finally:
            if pdf_in_temp: 
                shutil.rmtree(temp_folder)
        
        logging.info('process finished')
        
if __name__ == '__main__':
    import funcargparse
    from funcargparse import FuncArgParser
    parser = FuncArgParser()
    parser.setup_args(publish)
    parser.update_short(outformat='f')
    parser.update_short(outpath='o')    
    parser.update_short(dump_files='d')
    parser.update_short(create_pdf='pdf')    
    parser.create_arguments()
    parser.parse2func()
        
        
        