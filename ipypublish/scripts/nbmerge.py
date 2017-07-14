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

import nbformat

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key)
    
def merge_notebooks(directory, ignore_prefix='_'):
    
    merged = None
    for fname in natural_sort(glob.glob(os.path.join(directory,'*.ipynb'))):
        if os.path.basename(fname).startswith(ignore_prefix):
            continue
        with io.open(fname, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        if merged is None:
            merged = nb
        else:
            # TODO: add an optional marker between joined notebooks
            # like an horizontal rule, for example, or some other arbitrary
            # (user specified) markdown cell)
            merged.cells.extend(nb.cells)
    if not hasattr(merged.metadata, 'name'):
        merged.metadata.name = ''
    merged.metadata.name += "_merged"
    if (sys.version_info > (3, 0)):
        print(nbformat.writes(merged))
    else:
        print(nbformat.writes(merged).encode('utf-8'))

if __name__ == '__main__':
    notebooks = sys.argv[1]
    if not notebooks:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
        
    merge_notebooks(notebooks)