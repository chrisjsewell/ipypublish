.. _sphinx_extension:

Sphinx Extension
================

:py:mod:`ipypublish.ipysphinx` is adapted from
`nbshinx <https://nbsphinx.readthedocs.io>`_, to provide a
`sphinx extension <https://www.sphinx-doc.org/en/master/usage/extensions/>`_
for converting notebooks with :py:class:`ipypublish.convert.main.IpyPubMain`.

This entire website is built using it,
and a good example of using it would be to look at its conf.py.

The key addition to the configuration file (conf.py) is:

.. code-block:: python

    extensions = [
        'sphinx.ext.mathjax',
        'ipypublish.ipysphinx',
        'sphinxcontrib.bibtex'
    ]

.. important::

    To use the sphinx extension,
    IPyPublish must be installed with the sphinx extras:

    ``pip install ipypublish[sphinx]``

Additional configuration can be added,
as described in :numref:`tbl:sphinx_config`, and numbered figures etc can be
setup by adding:

.. code-block:: python

    numfig = True
    math_numfig = True
    numfig_secnum_depth = 2
    numfig_format: {'section': 'Section %s',
                    'figure': 'Fig. %s',
                    'table': 'Table %s',
                    'code-block': 'Code Block %s'}
    math_number_all = True

    mathjax_config = {
        'TeX': {'equationNumbers': {'autoNumber': 'AMS', 'useLabelIds': True}},
    }

.. important::

    To number items, the initial toctree must include the ``:numbered:`` option

.. table:: Configuration values to use in conf.py
    :name: tbl:sphinx_config

    ============================= =========================== ================================================
    Name                          Default                     Description
    ============================= =========================== ================================================
    ipysphinx_export_config       "sphinx_ipypublish_all.ext" ipypublish configuration file
    ipysphinx_folder_suffix       "_nbfiles"                  <fname><suffix> for dumping internal images, etc
    ipysphinx_overwrite_existing  False                       raise error if nb_name.rst already exists
    ipysphinx_config_folders      ()                          additional folders containing conversion files
    ipysphinx_show_prompts        False                       show cell prompts
    ipysphinx_input_prompt        "[%s]"                      format of input prompts
    ipysphinx_output_prompt       "[%s]"                      format of output prompts
    ============================= =========================== ================================================
