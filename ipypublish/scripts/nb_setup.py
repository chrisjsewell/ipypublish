"""
Some useful functions for creating
publishable jupyter notebooks

usage:

.. code-block:: python

    from ipypublish import nb_setup
    plt = nb_setup.setup_matplotlib(
        print_errors=True,
        output=('pdf',))
    pd = nb_setup.setup_pandas(escape_latex=True)
    sym = nb_setup.setup_sympy()
    import numpy as np
    from IPython.display import Image, Latex

"""
# Py2/Py3 compatibility
# =====================
# from __future__ import division as _division
# from __future__ import print_function as _print_function
import json
from io import BytesIO

# from IPython.display import Image, Latex

MPL_OPTIONS = (
    ('lines.linewidth', 1.5),
    ('lines.markeredgewidth', 1.0),
    ('lines.markersize', 8),
    ('lines.antialiased', True),
    ('lines.dashed_pattern', (3.7, 1.6)),
    ('lines.dashdot_pattern', (6.4, 1.6, 1, 1.6)),
    ('lines.dotted_pattern', [1, 1.65]),
    ('lines.scale_dashes', True),
    ('patch.linewidth', 1.0),
    ('patch.force_edgecolor', False),
    ('patch.antialiased', True),
    ('hatch.linewidth', 1.0),
    ('hist.bins', 10),
    ('boxplot.notch', False),
    ('boxplot.vertical', True),
    ('boxplot.whiskers', 1.5),
    ('boxplot.patchartist', False),
    ('boxplot.showmeans', False),
    ('boxplot.showcaps', True),
    ('boxplot.showbox', True),
    ('boxplot.showfliers', True),
    ('boxplot.meanline', False),
    ('boxplot.flierprops.markersize', 6),
    ('boxplot.flierprops.linewidth', 1.0),
    ('boxplot.boxprops.linewidth', 1.0),
    ('boxplot.whiskerprops.linewidth', 1.0),
    ('boxplot.capprops.linewidth', 1.0),
    ('boxplot.medianprops.linewidth', 1.0),
    ('boxplot.meanprops.markersize', 6),
    ('boxplot.meanprops.linewidth', 1.0),
    ('font.family', 'sans-serif'),
    ('font.serif', 'cm'),
    ('font.size', 16),
    ('text.usetex', True),
    # ('text.latex.unicode', False),
    ('text.latex.preamble', (
     '\\usepackage{subdepth}', '\\usepackage{type1cm}')),
    ('text.latex.preview', False),
    ('text.hinting_factor', 8),
    ('text.antialiased', True),
    ('mathtext.fallback_to_cm', True),
    ('image.lut', 256),
    ('image.resample', True),
    ('image.composite_image', True),
    ('contour.corner_mask', True),
    ('errorbar.capsize', 0),
    ('axes.labelsize', 18),
    ('axes.linewidth', 2.0),
    ('axes.spines.left', True),
    ('axes.spines.right', True),
    ('axes.spines.bottom', True),
    ('axes.spines.top', True),
    ('axes.titlesize', 20),
    ('axes.titlepad', 6.0),
    ('axes.grid', False),
    ('axes.labelpad', 4.0),
    ('axes.formatter.limits', (-7, 7)),
    ('axes.formatter.use_locale', False),
    ('axes.formatter.use_mathtext', False),
    ('axes.formatter.min_exponent', 0),
    ('axes.formatter.useoffset', True),
    ('axes.formatter.offset_threshold', 4),
    ('axes.unicode_minus', True),
    ('axes.xmargin', 0.05),
    ('axes.ymargin', 0.05),
    ('polaraxes.grid', True),
    ('axes3d.grid', True),
    ('legend.fontsize', 14),
    ('legend.fancybox', True),
    ('legend.numpoints', 1),
    ('legend.scatterpoints', 1),
    ('legend.markerscale', 1.0),
    ('legend.shadow', False),
    ('legend.frameon', True),
    ('legend.framealpha', 0.8),
    ('legend.borderpad', 0.4),
    ('legend.labelspacing', 0.5),
    ('legend.handlelength', 2.0),
    ('legend.handleheight', 0.7),
    ('legend.handletextpad', 0.8),
    ('legend.borderaxespad', 0.5),
    ('legend.columnspacing', 2.0),
    ('xtick.top', False),
    ('xtick.bottom', True),
    ('xtick.labeltop', False),
    ('xtick.labelbottom', True),
    ('xtick.major.size', 3.5),
    ('xtick.minor.size', 2),
    ('xtick.major.width', 0.8),
    ('xtick.minor.width', 0.6),
    ('xtick.major.pad', 3.5),
    ('xtick.minor.pad', 3.4),
    ('xtick.minor.visible', False),
    ('xtick.minor.top', True),
    ('xtick.minor.bottom', True),
    ('xtick.major.top', True),
    ('xtick.major.bottom', True),
    ('ytick.left', True),
    ('ytick.right', False),
    ('ytick.labelleft', True),
    ('ytick.labelright', False),
    ('ytick.major.size', 3.5),
    ('ytick.minor.size', 2),
    ('ytick.major.width', 0.8),
    ('ytick.minor.width', 0.6),
    ('ytick.major.pad', 3.5),
    ('ytick.minor.pad', 3.4),
    ('ytick.minor.visible', False),
    ('ytick.minor.left', True),
    ('ytick.minor.right', True),
    ('ytick.major.left', True),
    ('ytick.major.right', True),
    ('grid.linewidth', 0.8),
    ('grid.alpha', 1.0),
    ('figure.figsize', (6.4, 4.8)),
    ('figure.dpi', 100),
    ('figure.frameon', True),
    ('figure.autolayout', False),
    ('figure.max_open_warning', 20),
    ('figure.subplot.left', 0.125),
    ('figure.subplot.right', 0.9),
    ('figure.subplot.bottom', 0.11),
    ('figure.subplot.top', 0.88),
    ('figure.subplot.wspace', 0.2),
    ('figure.subplot.hspace', 0.2),
    ('figure.constrained_layout.use', False),
    ('figure.constrained_layout.hspace', 0.02),
    ('figure.constrained_layout.wspace', 0.02),
    ('figure.constrained_layout.h_pad', 0.04167),
    ('figure.constrained_layout.w_pad', 0.04167),
    ('savefig.frameon', True),
    ('savefig.jpeg_quality', 95),
    ('savefig.pad_inches', 0.1),
    ('savefig.transparent', False),
    ('savefig.dpi', 75),
    ('svg.image_inline', True),
    ('path.simplify', True),
    ('path.simplify_threshold', 0.1111111111111111),
    ('path.snap', True),
    ('path.effects', ()),
    ('agg.path.chunksize', 0),
    ('animation.embed_limit', 20),
    ('animation.bitrate', -1),
    ('animation.html_args', ()),
    ('animation.ffmpeg_args', ()),
    ('animation.avconv_args', ()),
    ('animation.convert_args', ())
)


def setup_matplotlib(
    output=('pdf', 'svg'),
    rcparams=None,
    usetex=True,
    print_errors=False
):
    """ import and setup matplotlib in the jupyter notebook

    Parameters
    ----------
    output: tuple[str]
        the output formats to save to the notebook
    rcparams: None or dict
        update default parameters set for matplotlib
    usetex: bool
        if True, and the 'latex' command is available,
        create figures with LaTeX
    print_errors: bool
        print errors for unavailable rcparams

    """
    from IPython import get_ipython
    from IPython.display import set_matplotlib_formats
    import matplotlib as mpl

    try:
        from shutil import which
    except ImportError:
        from shutilwhich import which

    ipython = get_ipython()
    latex_available = which('latex') is not None
    # if not latex_available:
    #     output = [o for o in output if o != "pdf"]

    set_matplotlib_formats(*output)
    ipython.magic("matplotlib inline")
    if 'svg' in output:
        ipython.magic("config InlineBackend.figure_format = 'svg'")

    final_params = dict(MPL_OPTIONS)
    if rcparams is not None:
        final_params.update(rcparams)
    if usetex and latex_available:
        final_params.update({'text.usetex': True})
    else:
        final_params.update({'text.usetex': False})

    keyerrors = []
    valerrors = {}
    for key, val in final_params.items():
        try:
            mpl.rcParams[key] = val
        except KeyError:
            keyerrors.append(key)
        except ValueError:
            valerrors[key] = val

    if print_errors:
        if keyerrors:
            print("KeyErrors:")
            for key in keyerrors:
                print("- key")
        if valerrors:
            print("ValueError:")
            print(json.dumps(valerrors, indent=2))

    return mpl.pyplot


def setup_pandas(escape_latex=False, use_longtable=False):
    """ import and setup pandas in the jupyter notebook

    Parameters
    ----------
    escape_latex: bool
        whether to escape special latex character, e.g. `_` -> `\\_`

    """
    import pandas as pd
    pd.set_option('display.latex.repr', True)
    pd.set_option('display.latex.longtable', use_longtable)
    pd.set_option('display.latex.escape', escape_latex)
    return pd


def setup_sympy():
    import sympy
    sympy.init_printing(use_latex=True)
    return sympy


def get_pimage():
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("to use this function; pip install pillow")
    return Image


def create_test_image(size=(50, 50)):
    file = BytesIO()
    image = get_pimage().new('RGBA', size=size, color=(155, 0, 0))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file


def images_read(paths):
    """read a list of image paths to a list of PIL.IMAGE instances """
    return [get_pimage().open(i).convert("RGBA") for i in paths]


def images_hconcat(images, width=700, height=700,
                   gap=0, aspaths=True):
    """concatenate multiple images horizontally

    Parameters
    ----------
    images : list
        if aspaths=True, list of path strings, else list of PIL.Image instances
    width : int or list[int]
        maximum width of final image, or of individual images
    height : int or list[int]
        maximum height of final image, or of individual images
    gap : int
        size of space between images

    Returns
    -------
    image : PIL.Image

    Examples
    --------
    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_hconcat([img_path,img_path])
    >>> img.size
    (100, 50)

    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_hconcat([img_path,img_path],width=40,height=40)
    >>> img.size
    (40, 20)

    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_hconcat([img_path,img_path],width=[40,30])
    >>> img.size
    (70, 40)

    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_hconcat([img_path,img_path],gap=10)
    >>> img.size
    (110, 50)

    """
    pimage = get_pimage()

    images = images_read(images) if aspaths else images
    if not isinstance(width, list):
        widths = [width for _ in images]
    else:
        widths = width[:]
        width = sum(widths) + gap * (len(images) - 1)
    if not isinstance(height, list):
        heights = [height for _ in images]
    else:
        heights = height[:]
        height = sum(heights)
    for im, w, h in zip(images, widths, heights):
        im.thumbnail((w, h), pimage.ANTIALIAS)
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths) + gap * (len(images) - 1)
    max_height = max(heights)
    new_im = pimage.new('RGBA', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0), mask=im)
        x_offset += im.size[0] + gap
    new_im.thumbnail((width, height), pimage.ANTIALIAS)
    return new_im


def images_vconcat(images, width=700, height=700,
                   gap=0, aspaths=True):
    """concatenate multiple images vertically

    Parameters
    ----------
    images : list
        if aspaths=True, list of path strings, else list of PIL.Image instances
    width : int or list[int]
        maximum width of final image, or of individual images
    height : int or list[int]
        maximum height of final image, or of individual images
    gap : int
        size of space between images

    Returns
    -------
    image : PIL.Image

    Examples
    --------
    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_vconcat([img_path,img_path])
    >>> img.size
    (50, 100)

    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_vconcat([img_path,img_path],width=40,height=40)
    >>> img.size
    (20, 40)

    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_vconcat([img_path,img_path],width=[40,30])
    >>> img.size
    (40, 70)

    >>> img_path = create_test_image(size=(50,50))
    >>> img = images_vconcat([img_path,img_path],gap=10)
    >>> img.size
    (50, 110)


    """
    pimage = get_pimage()

    images = images_read(images) if aspaths else images
    if not isinstance(width, list):
        widths = [width for _ in images]
    else:
        widths = width[:]
        width = sum(widths)
    if not isinstance(height, list):
        heights = [height for _ in images]
    else:
        heights = height[:]
        height = sum(heights) + gap * (len(images) - 1)
    for im, w, h in zip(images, widths, heights):
        im.thumbnail((w, h), pimage.ANTIALIAS)
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights) + gap * (len(images) - 1)
    new_im = pimage.new('RGBA', (max_width, total_height))
    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset), mask=im)
        y_offset += im.size[1] + gap
    new_im.thumbnail((width, height), pimage.ANTIALIAS)
    return new_im


def images_gridconcat(pathslist, width=700, height=700,
                      aspaths=True, hgap=0, vgap=0):
    """concatenate multiple images in a grid

    Parameters
    ----------
    pathslist : list[list]
        if aspaths=True, list of path strings, else list of PIL.Image instances
        each sub list constitutes a row
    width : int
        maximum width of final image
    height : int
        maximum height of final image
    hgap : int
        size of horizontal space between images
    vgap : int
        size of vertical space between images

    Returns
    -------
    image : PIL.Image

    """
    pimage = get_pimage()
    himages = [images_hconcat(paths, gap=hgap, aspaths=aspaths)
               for paths in pathslist]
    new_im = images_vconcat(himages, gap=vgap, aspaths=False)
    new_im.thumbnail((width, height), pimage.ANTIALIAS)
    return new_im


if __name__ == "__main__":
    import matplotlib as mpl
    print(json.dumps({
        k: v[0]
        for k, v in mpl.rcsetup.defaultParams.items()
        if isinstance(v[0], (int, float, list, tuple, set))}, indent=2))
