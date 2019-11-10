Developer Guide
+++++++++++++++

Installation
~~~~~~~~~~~~

To install the development version::

    >> git clone https://github.com/chrisjsewell/ipypublish .
    >> cd ipypublish

and either use the pre-written Conda development environment (recommended)::

    >> conda env create -n ipub_testenv -f conda_dev_env.yaml python=3.6
    >> conda activate ipub_testenv
    >> pip install --no-deps -e .

or install all *via* pip::

    >> pip install -e .[tests]

Testing
~~~~~~~

|Build Status| |Coverage Status|

The following will discover and run all unit test:

.. code:: shell

   >> cd ipypublish
   >> pytest -v

Coding Style Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~

The code style is tested using `flake8 <http://flake8.pycqa.org>`__,
with the configuration set in ``.flake8``, and code should be formatted
with `black <https://github.com/ambv/black>`__.

Installing with ``ipypublish[code_style]`` makes the
`pre-commit <https://pre-commit.com/>`__ package available, which will
ensure these tests are passed by reformatting the code and testing for
lint errors before submitting a commit. It can be set-up by:

.. code:: shell

   >> cd ipypublish
   >> pre-commit install

Optionally you can run ``black`` and ``flake8`` separately:

.. code:: shell

   >> black path/to/file
   >> flake8

Editors like VS Code also have automatic code reformat utilities, which
can check and adhere to this standard.

Documentation
~~~~~~~~~~~~~

The documentation can be created locally by:

.. code:: shell

   >> cd ipypublish/docs
   >> make clean
   >> make  # or make debug

.. |Build Status| image:: https://travis-ci.org/chrisjsewell/ipypublish.svg?branch=master
   :target: https://travis-ci.org/chrisjsewell/ipypublish
.. |Coverage Status| image:: https://coveralls.io/repos/github/chrisjsewell/ipypublish/badge.svg?branch=master
   :target: https://coveralls.io/github/chrisjsewell/ipypublish?branch=master
