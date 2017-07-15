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
        
from ipypublish import scripts
from ipypublish.scripts.nbmerge import merge_notebooks
from ipypublish.scripts.nbexport import export_notebook
from ipypublish.scripts.pdfexport import export_pdf

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
              
    Examples
    --------
              
    
    """
    if isinstance(ipynb_path,basestring):
        ipynb_path = pathlib.Path(ipynb_path)
    ipynb_name = ipynb_path.name.split('.')[0]
    files_folder = ipynb_name+'_files'

    outdir = os.path.join(os.getcwd(),'converted') if outpath is None else outpath 
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    slogger = logging.StreamHandler(sys.stdout)
    slogger.setLevel(getattr(logging,loglevel.upper()))
    formatter = logging.Formatter('%(levelname)s:%(module)s:%(message)s')
    slogger.setFormatter(formatter)
    root.addHandler(slogger)
    flogger = logging.FileHandler(os.path.join(outdir,ipynb_name+'.nbpub.log'), 'w')
    flogger.setLevel(getattr(logging,loglevel.upper()))
    root.addHandler(flogger)
    
    logging.info('started ipypublish at {0}'.format(time.strftime("%c")))
    logging.info('logging to: {}'.format(os.path.join(outdir,ipynb_name+'.nbpub.log')))    
    logging.info('running for ipynb(s) at: {0}'.format(ipynb_path))
    logging.info('with conversion: {0}'.format(outformat))
    
    final_nb, meta_path = merge_notebooks(ipynb_path,
                        ignore_prefix=ignore_prefix)
    logging.debug('notebooks meta path: {}'.format(meta_path))

    # retrieve external file paths from metadata,
    # resolving where they are, if the path is relative
    # make sure that the link points to a single folder

    logging.info('resolving external file paths')

    external_files = []
    # TODO do this individually for known keys in metadata, but should come up with more consistent method
    if hasattr(final_nb.metadata, 'latex_doc'):
                
        if hasattr(final_nb.metadata.latex_doc, 'files'):
            mfiles = []
            for fpath in final_nb.metadata.latex_doc.files:
                fpath = resolve_path(fpath, meta_path)
                if not os.path.exists(fpath):
                    logging.warning('file in metadata does not exist'
                                    ': {}'.format(fpath))
                else:
                    external_files.append(fpath)
                mfiles.append(os.path.join(files_folder, os.path.basename(fpath)))   

            final_nb.metadata.latex_doc.files = mfiles
        
        if hasattr(final_nb.metadata.latex_doc, 'bibliography'):                    
            bib = final_nb.metadata.latex_doc.bibliography
            bib = resolve_path(bib, meta_path)
            if not os.path.exists(bib):
                logging.warning('bib in metadata does not exist'
                                ': {}'.format(bib))
            else:
                external_files.append(bib)

            final_nb.metadata.latex_doc.bibliography = os.path.join(files_folder,
                                                            os.path.basename(bib))
            
        if hasattr(final_nb.metadata.latex_doc, 'titlepage'):
            if hasattr(final_nb.metadata.latex_doc.titlepage, 'logo'):
                logo = final_nb.metadata.latex_doc.titlepage.logo
                logo = resolve_path(logo, meta_path)
                if not os.path.exists(logo):
                    logging.warning('logo in metadata does not exist'
                                    ': {}'.format(logo))
                else:
                    external_files.append(logo)

                final_nb.metadata.latex_doc.titlepage.logo = os.path.join(files_folder,
                                                            os.path.basename(logo))

    logging.info('getting output format from exporter plugin')
    try:
        outplugin = getattr(scripts, outformat)
    except AttributeError as err:
        logging.error('the exporter plugin does not exist: {}'.format(outformat))
        raise ValueError('the exporter plugin does not exist: {}'.format(outformat))
        
    oformat = outplugin.oformat
    otemplate = outplugin.template
    oconfig = outplugin.config
    # ensure file paths point towards the right folder
    oconfig['ExtractOutputPreprocessor.output_filename_template'] = files_folder+'/{unique_key}_{cell_index}_{index}{extension}'
    
    (body, resources), exe = export_notebook(final_nb, oformat,oconfig,otemplate)

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
        for external_path in external_files:
            shutil.copyfile(external_path,
                os.path.join(outfilespath,os.path.basename(external_path)))
     
    if create_pdf and oformat.lower()=='latex':
        logging.info('running pdf conversion')   
        
        export_pdf(outpath, outdir=outdir, 
                   files_path=outfilespath,
                   convert_in_temp=pdf_in_temp,
                   html_viewer=True,
                   debug_mode=pdf_debug)
        
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
        
        
        