
def default_conf():
    """ a default sphinx configuration file

    This file is execfile()d by Sphinx,
    with the current directory set to its containing dir

    .. seealso::

        http://www.sphinx-doc.org/en/master/usage/configuration.html

    """
    needs_sphinx = '1.6'  # noqa: F841

    master_doc = 'index'  # noqa: F841
    source_suffix = ['.rst']  # noqa: F841

    # Exclude build directory and Jupyter backup files:
    exclude_patterns = [  # noqa: F841
        '_build', 'build',
        '**.ipynb_checkpoints']

    # Set required extensions, to render particular directives etc
    extensions = [   # noqa: F841
        'ipypublish.sphinx',
        'sphinx.ext.mathjax',
        'sphinxcontrib.bibtex',
        'sphinx.ext.todo',
        'sphinx.ext.imgconverter'
    ]

    # html_theme = 'alabaster'

    ## Extension options # noqa: E266

    # If true, `todo` and `todoList` produce output, else they produce nothing.
    todo_include_todos = False  # noqa: F841

    # allow figures to be numbered
    numfig = True   # noqa: F841
    math_numfig = True  # noqa: F841
    numfig_secnum_depth = 2
    # numfig_format = {'section': 'Section %s'),
    #                  'figure': 'Fig. %s'),
    #                  'table': 'Table %s',
    #                  'code-block': 'Listing %s'}
    # math_eqref_format = "eq.{number}"  # TODO this isn't working

    linkcheck_ignore = [r'http://localhost:\d+/']  # noqa: F841

    # List of arguments to be passed to the kernel that executes the notebooks:
    nbsphinx_execute_arguments = [  # noqa: F841
        "--InlineBackend.figure_formats={'svg', 'pdf'}",
        "--InlineBackend.rc={'figure.dpi': 96}",
    ]


if __name__ == "__main__":

    import inspect
    lines = inspect.getsource(default_conf)

    # >> rm -r build/
    # >> sphinx-build -b html . build/html

# .. toctree::
#    :includehidden:
#    :maxdepth: 3
#    :numbered:
#    :caption: Table of Contents:

#    notebook_name

# project = u'ipypublish'
# author = u'Chris Sewell'
# description = ('Create quality publication and presentation'
#                'directly from Jupyter Notebook(s)')
