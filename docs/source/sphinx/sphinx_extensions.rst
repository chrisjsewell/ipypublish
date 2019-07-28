.. _sphinx_extensions:

Introduction
============

IPyPublish packages a number of `sphinx <http://www.sphinx-doc.org>`_
extensions which are used to convert notebooks to (primarily) HTML.

.. tip::

    To convert a notebook directly to HTML *via* sphinx,
    you can run:

    ``nbpublish -f sphinx_ipypublish_main.run notebook.ipynb``

    This will convert the notebook to .rst, create a basic conf.py file
    (including the ipypublish extensions), and
    call `sphinx-build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html>`_.
