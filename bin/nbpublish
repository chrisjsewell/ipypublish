#!/usr/bin/env python
from ipypublish.main import publish
                
def nbpublish(ipynb_path,
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
              
    """
    return publish(ipynb_path,
                  outformat=outformat,
                  outpath=outpath, dump_files=dump_files,
                  ignore_prefix=ignore_prefix,
                  create_pdf=create_pdf, pdf_in_temp=pdf_in_temp, pdf_debug=pdf_debug,
                  loglevel=loglevel) 
                         
if __name__ == '__main__':
    import funcargparse
    from funcargparse import FuncArgParser
    parser = FuncArgParser()
    parser.setup_args(nbpublish)
    parser.update_short(outformat='f')
    parser.update_short(outpath='o')    
    parser.update_short(dump_files='d')
    parser.update_short(create_pdf='pdf')    
    parser.create_arguments()
    parser.parse2func()
        
        
        