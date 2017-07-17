#!/usr/bin/env python
import os, sys
import time
import re
#import base64
import logging
import shutil

# python 3 to 2 compatibility
try:
    basestring
except NameError:
    basestring = str
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
        
from ipypublish.scripts import export_plugins
from ipypublish.scripts.nbmerge import merge_notebooks
from ipypublish.scripts.nbexport import export_notebook
from ipypublish.scripts.pdfexport import export_pdf
                
def publish(ipynb_path,
            outformat='latex_ipypublish_main',
            outpath=None, dump_files=False,
            ignore_prefix='_',
            create_pdf=False, pdf_in_temp=False, pdf_debug=False):
    """ convert one or more Jupyter notebooks to a published format

    paths can be string of an existing file or folder,
    or a pathlib.Path like object
            
    all files linked in the documents are placed into a single folder
              
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
              
    Returns
    --------
    outpath: str
     path to output file   
    
    """
    if isinstance(ipynb_path,basestring):
        ipynb_path = pathlib.Path(ipynb_path)
    ipynb_name = ipynb_path.name.split('.')[0]
    files_folder = ipynb_name+'_files'

    outdir = os.path.join(os.getcwd(),'converted') if outpath is None else outpath 
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    
    logging.info('started ipypublish at {0}'.format(time.strftime("%c")))
    logging.info('logging to: {}'.format(os.path.join(outdir,ipynb_name+'.nbpub.log')))    
    logging.info('running for ipynb(s) at: {0}'.format(ipynb_path))
    logging.info('with conversion: {0}'.format(outformat))
    
    final_nb, meta_path = merge_notebooks(ipynb_path,
                        ignore_prefix=ignore_prefix)
    logging.debug('notebooks meta path: {}'.format(meta_path))

    logging.info('getting output format from exporter plugin')
    plugins = export_plugins.get()
    if not outformat in plugins:
        logging.error("the exporter plugin '{}' does not exist".format(outformat)
                      +", acceptable names: {}".format(list(plugins.keys())))
        raise ValueError("the exporter plugin '{}' does not exist".format(outformat)
                      +", acceptable names: {}".format(list(plugins.keys())))
    oplugin = plugins[outformat]
        
    # ensure file paths point towards the right folder
    oplugin['config']['ExtractOutputPreprocessor.output_filename_template'] = files_folder+'/{unique_key}_{cell_index}_{index}{extension}'
    oplugin['config']['LatexDocLinks.metapath'] = str(meta_path)
    oplugin['config']['LatexDocLinks.filesfolder'] = str(files_folder)

    logging.debug('{}'.format(oplugin['config']))
    
    ##for debugging
    # tpath = os.path.join(outdir, ipynb_name+'.template.tpl')
    # with open(tpath, "w") as fh:
    #     fh.write(str(oplugin['template']))
    
    (body, resources), exe = export_notebook(final_nb, 
                             oplugin['oformat'],oplugin['config'],oplugin['template'])

    # reduce multiple blank lines to single
    body = re.sub(r'\n\s*\n', '\n\n', body) 

    # filter internal files by those that are referenced in the document body
    if resources['outputs']:
        for path in list(resources['outputs'].keys()):
            if not path in body:
                resources['outputs'].pop(path)                
        internal_files = resources['outputs']
    else:
        internal_files = {}
    
    # output main file    
    outpath = os.path.join(outdir,ipynb_name+exe)
    logging.info('outputting converted file to: {}'.format(outpath))    
    with open(outpath, "w") as fh:
        fh.write(body)

    # output external files
    if dump_files or create_pdf:
        outfilespath = os.path.join(outdir,files_folder)
        logging.info('dumping external files to: {}'.format(outfilespath))    
        
        if os.path.exists(outfilespath):
            shutil.rmtree(outfilespath)
        os.mkdir(outfilespath)
            
        for internal_path, fcontents in internal_files.items():
            with open(os.path.join(outdir, internal_path), "wb") as fh:
                fh.write(fcontents)
        for external_path in resources['external_file_paths']:
            shutil.copyfile(external_path,
                os.path.join(outfilespath,os.path.basename(external_path)))
     
    if create_pdf and oplugin['oformat'].lower()=='latex':
        logging.info('running pdf conversion')   
        
        if not export_pdf(outpath, outdir=outdir, 
                   files_path=outfilespath,
                   convert_in_temp=pdf_in_temp,
                   html_viewer=True,
                   debug_mode=pdf_debug):
            logging.error('pdf export returned false, try running with pdf_debug=True')
            raise RuntimeError('the pdf export failed, try running with pdf_debug=True')
        
    logging.info('process finished successfully')
    return outpath
        
        
        
        