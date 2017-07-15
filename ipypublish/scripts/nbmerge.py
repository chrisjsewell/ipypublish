#!/usr/bin/env python
# Note, updated version of 
# https://github.com/ipython/ipython-in-depth/blob/master/tools/nbmerge.py
"""
usage:

python nbmerge.py directory_name > merged.ipynb
"""
from __future__ import print_function

import io
import os
import sys
import glob
import re
import logging

import nbformat

# python 3 to 2 compatibility
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
try:
    basestring
except NameError:
    basestring = str

def alphanumeric_sort(l): 
    """sort key.name alphanumeriacally """
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key.name) ] 
    return sorted(l, key = alphanum_key)

def merge_notebooks(ipynb_path, ignore_prefix='_',
                    to_str=False, as_version=4):
    """ merge one or more ipynb's, 
    if more than one, then the meta data is taken from the first 
    
    Parameters
    ----------
    ipynb_path: str or path_like                
        
    Returns
    ------
    finalnb: jupyter.notebook
    meta_path : pathlib.Path
        path to notebook containing meta file

    """
                    
    if isinstance(ipynb_path,basestring):
        ipynb_path = pathlib.Path(ipynb_path)
    if not ipynb_path.exists():
        logging.error('the notebook path does not exist: {}'.format(ipynb_path))
        raise IOError('the notebook path does not exist: {}'.format(ipynb_path))
    
    final_nb = None
    if ipynb_path.is_dir():
        logging.info('Merging all notebooks in directory')
        for ipath in alphanumeric_sort(ipynb_path.glob('*.ipynb')):
            if os.path.basename(ipath.name).startswith(ignore_prefix):
                continue
            with ipath.open('r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=as_version)
            if final_nb is None:
                meta_path = ipath
                final_nb = nb
            else:
                final_nb.cells.extend(nb.cells)
    else:
        logging.info('Reading notebook')
        with ipynb_path.open('r', encoding='utf-8') as f:
            final_nb = nbformat.read(f, as_version=as_version)
        meta_path = ipynb_path
    if not hasattr(final_nb.metadata, 'name'):
        final_nb.metadata.name = ''
    final_nb.metadata.name += "_merged"                

    if to_str:
        if (sys.version_info > (3, 0)):
            return nbformat.writes(final_nb)
        else:
            return nbformat.writes(final_nb).encode('utf-8')
    
    if final_nb is None:
        logging.error('no acceptable notebooks found for path: {}'.format(ipynb_path.name))
        raise IOError('no acceptable notebooks found for path: {}'.format(ipynb_path.name))
    
    return final_nb, meta_path
