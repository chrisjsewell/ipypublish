Getting Started
===============

Installation
------------

Using `Conda <https://conda.io/docs/>`__ is recommended for package
management, in order to create self contained environments with specific
versions of packages. The main external packages required are the
Jupyter notebook and `Pandoc <http://pandoc.org>`__ (for conversion
between file formats):

.. code-block:: console

   conda create --name ipyreport -c conda-forge jupyter pandoc

ipypublish can then be installed into this environment:

.. code-block:: console

   source activate ipyreport
   pip install ipypublish

For converting to PDF, the TeX document preparation ecosystem is
required, in particular
`latexmk <http://mg.readthedocs.io/latexmk.html>`__), which can be
installed from:

-  Linux: `TeX Live <http://tug.org/texlive/>`__
-  macOS (OS X): `MacTeX <http://tug.org/mactex/>`__
-  Windows: `MikTex <http://www.miktex.org/>`__

For helpful extensions to the notebooks core capabilities, see the
`Jupyter Notebook Extensions
package <http://jupyter-contrib-nbextensions.readthedocs.io/en/latest/>`__:

.. code-block:: console

   conda install --name ipyreport jupyter_contrib_nbextensions

Additionally, a more extensive setup of useful packages (used to create
the examples) are provided by the
`anaconda distribution <https://docs.anaconda.com/anaconda/packages/pkg-docs/>`__
which can be installed in to a new environment

.. code-block:: console

   conda create --name ipyreport anaconda

Basic Conversion
----------------

The **nbpublish** script handles parsing the notebooks to nbconvert,
with the appropriate converter.

.. code-block:: console

   nbpublish -h
   nbpublish -pdf -f latex_ipypublish_nocode path/to/notebook.ipynb

For a more detailed explanation see the :ref:`notebook_conversion` section.

The **nbpresent** script handles serving
`reveal.js <http://lab.hakim.se/reveal-js/#/>`__ slides to a webbrowser.

.. code-block:: console

   nbpresent -h
   nbpresent -f slides_ipypublish_nocode path/to/notebook.ipynb

Note that, for offline use, simply download the latest version of
reveal.js `here <https://github.com/hakimel/reveal.js/releases>`__,
rename the entire folder to reveal.js and place it in the same folder as
the converted .slides.html file. The slides can also be save to PDF my
appending ``pdf-export`` to the url (see
`here <https://github.com/hakimel/reveal.js#pdf-export>`__ for details).

Troubleshooting
---------------

For installation issues, `Travis
CI <https://en.wikipedia.org/wiki/Travis_CI>`__ is used to automatically
test updates against python 2.7 and 3.6, for both Linux and OSX,
Therefore, to troubleshoot any installation/run issues, it is best to
first look at the `travis
config <https://github.com/chrisjsewell/ipypublish/blob/master/.travis.yml>`__
and `travis test runs <https://travis-ci.org/chrisjsewell/ipypublish>`__
for working configurations.

The `requirements-lock.txt <https://github.com/chrisjsewell/ipypublish/blob/master/requirements-lock.txt>`_
file can also be used to provide exact versions of
working package dependencies.

For conversion issues, for both ``nbpublish`` and ``nbpresent``,
detailed log messages of the run are output to both the console and file
(default path: converted/notebook_name.nbpub.log). To debug conversions,
use the ``--log-level debug`` and ``--pdf-debug`` flags. If there is
still an error, please raise an issue on the `GitHub
repository <https://github.com/chrisjsewell/ipypublish/issues>`__,
including the run environment and the log file.