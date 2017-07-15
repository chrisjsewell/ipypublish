#!/usr/bin/env python
"""
Some setup for improved latex/pdf output

at top of workbook, use

    from ipynb_latex_setup import *

"""

# Py2/Py3 compatibility
# =====================
from __future__ import print_function as _print_function
from __future__ import division as _division

# PYTHON
# =======
from collections import OrderedDict

# IPYTHON
# =======
try:
    from IPython import get_ipython
    from IPython.display import Image, Latex
    from IPython.display import set_matplotlib_formats
    _ipy_present = True
except ImportError:
    _ipy_present = False
if _ipy_present:
    ipython = get_ipython()
    if ipython is not None:
        ipython.magic("config InlineBackend.figure_format = 'svg'")
        ipython.magic("matplotlib inline")
        set_matplotlib_formats('pdf', 'svg')

# NUMPY
# =====
try:
    import numpy as np
except NameError:
    pass

# MATPLOTLIB
# ===========
try:
    import matplotlib as mpl
    _mpl_present = True
except ImportError:
    _mpl_present = False
    
if _mpl_present:
    import matplotlib.pyplot as plt
    mpl.rcParams['savefig.dpi'] = 75
    mpl.rcParams['figure.figsize'] = (7, 4)
    mpl.rcParams['figure.autolayout'] = False
    mpl.rcParams['axes.labelsize'] = 18
    mpl.rcParams['axes.titlesize'] = 20
    mpl.rcParams['font.size'] = 16
    mpl.rcParams['lines.linewidth'] = 2.0
    mpl.rcParams['lines.markersize'] = 8
    mpl.rcParams['legend.fontsize'] = 14
    mpl.rcParams['text.usetex'] = True
    mpl.rcParams['font.family'] = "serif"
    mpl.rcParams['font.serif'] = "cm"
    mpl.rcParams['text.latex.preamble'] = r"\usepackage{subdepth}, \usepackage{type1cm}"

# PANDAS
# ======
try:
    import pandas as pd
    _pandas_present = True
except ImportError:
    _pandas_present = False

if _pandas_present and ipython:
    pd.set_option('display.latex.repr',True)
    pd.set_option('display.latex.longtable',False)
    pd.set_option('display.latex.escape',False)

# SYMPY
# =====
try:
    import sympy as sym
    _sympy_present = True
except ImportError:
    _sympy_present = False
if _sympy_present:
    sym.init_printing(use_latex=True)

# IMAGE ARRANGEMENT with PIL
# ==========================
try:
    from PIL import Image as PImage
    _pil_present = True
except ImportError:
    _pil_present = False
if _pil_present:
    def images_read(paths):
        """read a list of image paths to a list of PIL.IMAGE instances """
        return [PImage.open(i).convert("RGBA") for i in paths]
    def images_hconcat(images, width=700,height=700, 
                       gap=0,aspaths=True):
        """concatenate multiple images horizontally 
    
        Properties
        ----------
        images : list
            if aspaths=True, list of path strings, else list of PIL.Image instances
        gap : int
            size of space between images
    
        Returns
        -------
        image : PIL.Image
                   
        """
        images = images_read(images) if aspaths else images
        if not isinstance(width,list):
            widths = [width for _ in images] 
        else:
            widths = width[:]
            width = sum(widths)
        if not isinstance(height,list):
            heights = [height for _ in images]
        else:
            heights = height[:]
            height = sum(heights) + gap*(len(images)-1)
        for im,w,h in zip(images,widths,heights):
            im.thumbnail((w,h), PImage.ANTIALIAS)
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths) + gap*len(images)
        max_height = max(heights)
        new_im = PImage.new('RGBA', (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0),mask=im)
            x_offset += im.size[0] + gap
        new_im.thumbnail((width,height), PImage.ANTIALIAS)
        return new_im

    def images_vconcat(images, width=700,height=700, 
                       gap=0, aspaths=True):
        """concatenate multiple images vertically 
    
        Properties
        ----------
        images : list
            if aspaths=True, list of path strings, else list of PIL.Image instances
        width : int or list of ints
            if a list, must be same length as number of images
        height : int or list of ints
            if a list, must be same length as number of images
        gap : int
            size of space between images
    
        Returns
        -------
        image : PIL.Image
                   
        """
        images = images_read(images) if aspaths else images
        if not isinstance(width,list):
            widths = [width for _ in images] 
        else:
            widths = width[:]
            width = sum(widths)
        if not isinstance(height,list):
            heights = [height for _ in images]
        else:
            heights = height[:]
            height = sum(heights) + gap*(len(images)-1)
        for im,w,h in zip(images,widths,heights):
            im.thumbnail((w,h), PImage.ANTIALIAS)
        widths, heights = zip(*(i.size for i in images))
        max_width = max(widths)
        total_height = sum(heights) + gap*len(images)
        new_im = PImage.new('RGBA', (max_width, total_height))
        y_offset = 0
        for im in images:
            new_im.paste(im, (0,y_offset),mask=im)
            y_offset += im.size[1] + gap
        new_im.thumbnail((width,height), PImage.ANTIALIAS)
        return new_im

    def images_gridconcat(pathslist,width=700,height=700,
                         aspaths=True,hgap=0,vgap=0):
        """concatenate multiple images in a grid 
    
        Properties
        ----------
        pathslist : list of lists
            if aspaths=True, list of path strings, else list of PIL.Image instances
            each sub list constitutes a row
        hgap : int
            size of horizontal space between images
        hgap : int
            size of vertical space between images
    
        Returns
        -------
        image : PIL.Image
                   
        """
        himages = [images_hconcat(paths,gap=hgap,aspaths=aspaths) for paths in pathslist]
        new_im = images_vconcat(himages,gap=vgap,aspaths=False)
        new_im.thumbnail((width,height), PImage.ANTIALIAS)
        return new_im

# JSONEXTENDED
# ==========================
try:
    from jsonextended import ejson, edict
    _jsonextended_present = True
except ImportError:
    _jsonextended_present = False
if _jsonextended_present:
    from jsonextended import plugins as eplugins
    eplugins.load_builtin_plugins()

