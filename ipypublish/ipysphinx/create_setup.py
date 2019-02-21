
import os
import logging
from six import string_types
from ipypublish.utils import read_file_from_directory

logger = logging.getLogger("make-conf")


def make_conf(overwrite=False, **kwargs):
    """ create the contents of a sphinx config.py
    with default values compliant with ipypublish.

    Parameters
    ----------
    overwrite: bool
        if True, default arguments are overwritten by key-word arguments
    kwargs:
        key-word arguments are included as <key> = <val>
        note docstring is a special key, inserted at the top of the file

    Returns
    -------
    conf_content: str

    """

    # load local config.yaml
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    data = read_file_from_directory(
        path, 'config.yaml', 'sphinx config', logger, interp_ext=True)

    conf_str = []

    docstring = None
    if "docstring" in data:
        docstring = data.pop("docstring")

    if "docstring" in kwargs:
        kwdocstring = data.pop("docstring")
        if overwrite or not docstring:
            docstring = kwdocstring

    if docstring:
        conf_str.append('"""')
        conf_str.append(str(docstring))
        conf_str.append('"""')

    for key, val in data.items():
        if key in kwargs and overwrite:
            continue
        conf_str.append('')
        if isinstance(val, string_types):
            val = '"{}"'.format(val)
        conf_str.append('{0} = {1}'.format(key, val))

    for key, val in kwargs.items():
        if key in data and not overwrite:
            continue
        conf_str.append('')
        if isinstance(val, string_types):
            val = '"{}"'.format(val)
        conf_str.append('{0} = {1}'.format(key, val))

    return "\n".join(conf_str) + "\n"


def make_index(toc_files, toc_depth=3, toc_title="Table of Contents",
               toc_numbered=True, toc_glob=False,
               header=None,
               prolog=None, epilog=None):
    """ make an index file, containing a toc tree

    Parameters
    ----------
    toc_files: list[str]
        list of file paths (relative to the index)
        to be included in the toc tree
    toc_depth=3: int
        depth of toc tree
    toc_title: str
        title of toc tree
    toc_numbered=True: bool
        number sections and figures, tables, etc
    header: None or str
    prolog: None or str
    epilog: None or str

    Returns
    -------
    index_content: str

    """
    if not toc_files:
        raise AssertionError("there must be at lease on toc file")

    index_str = []

    if header:
        index_str.append(str(header))
        index_str.append('='*len(str(header)))
        index_str.append('')

    if prolog:
        index_str.append(str(prolog))
        index_str.append('')

    index_str.append(".. toctree::")
    index_str.append("   :includehidden:")
    index_str.append("   :maxdepth: {}".format(toc_depth))
    if toc_numbered:
        index_str.append("   :numbered:")
    if toc_glob:
        index_str.append("   :glob:")
    index_str.append("   :caption: {}:".format(toc_title))
    index_str.append('')

    for toc_file in toc_files:
        index_str.append("   " + os.path.splitext(toc_file)[0].lstrip())

    if epilog:
        index_str.append('')
        index_str.append(str(epilog))

    return "\n".join(index_str) + "\n"


if __name__ == "__main__":

    print(make_conf(
        project='ipypublish',
        author='Chris Sewell',
        description=('Create quality publication and presentation'
                     'directly from Jupyter Notebook(s)')
    ))

    print(make_index(['path/to/file.rst'], header="Header"))
