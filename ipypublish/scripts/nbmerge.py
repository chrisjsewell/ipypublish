#!/usr/bin/env python
# Note, updated version of
# https://github.com/ipython/ipython-in-depth/blob/master/tools/nbmerge.py
"""
usage:

python nbmerge.py directory_name > merged.ipynb
"""
from __future__ import print_function

import logging
import os
import re
import sys

import nbformat
from six import string_types

from ipypublish.utils import pathlib


def alphanumeric_sort(l):
    """sort key.name alphanumerically

    Parameters
    ----------
    l: list[str]

    """
    def convert(text): return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key.name)]
    return sorted(l, key=alphanum_key)


def merge_notebooks(ipynb_path, ignore_prefix='_',
                    to_str=False, as_version=4):
    """ merge one or more ipynb's,
    if more than one, then the meta data is taken from the first

    Parameters
    ----------
    ipynb_path: str or pathlib.Path
    ignore_prefix : str
        ignore filename starting with this prefix
    to_str: bool
        return as a string, else return nbformat object
    as_version: int
        notebook format vesion

    Returns
    ------
    finalnb: jupyter.notebook
    meta_path : pathlib.Path
        path to notebook containing meta file

    """
    meta_path = ''
    if isinstance(ipynb_path, string_types):
        ipynb_path = pathlib.Path(ipynb_path)
    if not ipynb_path.exists():
        logging.error('the notebook path does not exist: {}'.format(
            ipynb_path))
        raise IOError('the notebook path does not exist: {}'.format(
            ipynb_path))

    final_nb = None
    if ipynb_path.is_dir():
        logging.info('Merging all notebooks in directory')
        for ipath in alphanumeric_sort(ipynb_path.glob('*.ipynb')):
            if os.path.basename(ipath.name).startswith(ignore_prefix):
                continue
            with ipath.open('r', encoding='utf-8') as f:
                if (sys.version_info.major == 3
                    and sys.version_info.minor < 6
                        and "win" not in sys.platform):
                    data = f.read()
                    if hasattr(data, "decode"):
                        data = data.decode("utf-8")
                    nb = nbformat.reads(data, as_version=as_version)
                else:
                    nb = nbformat.read(f, as_version=as_version)
            if final_nb is None:
                meta_path = ipath
                final_nb = nb
            else:
                final_nb.cells.extend(nb.cells)
    else:
        logging.info('Reading notebook')
        with ipynb_path.open('r', encoding='utf-8') as f:
            if (sys.version_info.major == 3
                and sys.version_info.minor < 6
                    and "win" not in sys.platform):
                data = f.read()
                if hasattr(data, "decode"):
                    data = data.decode("utf-8")
                final_nb = nbformat.reads(data, as_version=as_version)
            else:
                final_nb = nbformat.read(f, as_version=as_version)
        meta_path = ipynb_path
    if not hasattr(final_nb.metadata, 'name'):
        final_nb.metadata.name = ''
    final_nb.metadata.name += "_merged"

    if to_str:
        if sys.version_info > (3, 0):
            return nbformat.writes(final_nb)
        else:
            return nbformat.writes(final_nb).encode('utf-8')

    if final_nb is None:
        logging.error('no acceptable notebooks found for path: {}'.format(
            ipynb_path.name))
        raise IOError('no acceptable notebooks found for path: {}'.format(
            ipynb_path.name))

    return final_nb, meta_path
