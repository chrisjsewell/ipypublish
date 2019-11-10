.. _sphinx_ext_gls:

ipypublish.sphinx.gls
=====================

:py:mod:`ipypublish.sphinx.gls` is adapted from
`sphinxcontrib-bibtex <https://sphinxcontrib-bibtex.readthedocs.io>`_,
to provide a
`sphinx extension <https://www.sphinx-doc.org/en/master/usage/extensions/>`_
that closely replicates the functionality of the
`LaTeX glossaries <https://ctan.org/pkg/glossaries>`_ package,
for referencing glossaries terms, acronyms and symbols
provided in a separate file.

This extension loads:

- The ``bibglossary`` directive, for setting a file containing terms
  (see :py:mod:`ipypublish.sphinx.gls.directives`)
- ``gls``, ``glsc``, ``glspl``, ``glscpl`` roles, for referencing the terms
  (see :py:mod:`ipypublish.sphinx.gls.roles`)

.. seealso::

    :ref:`RMarkdown References <markdown_references>`,
    for an example of using this extension
    within the conversion of a Jupyter Notebook.

Installation
------------

Install ipypublish:

.. code-block:: console

    conda install "ipypublish>=0.10"

or

.. code-block:: console

    pip install "ipypublish[sphinx]>=0.10"

The key addition to the sphinx configuration file (conf.py) is:

.. code-block:: python

    extensions = [
        'ipypublish.sphinx.gls'
    ]

Also ``sphinx.ext.mathjax`` is recommended for rendering math.

The Glossary File Formats
-------------------------

The glossary file can be in one of two formats;
a .bib file (recommended) or a .tex file.

The .bib file is a standard `BibTeX <http://www.bibtex.org/Format/>`_ file
(which is initially parsed by
`bibtexparser <https://bibtexparser.readthedocs.io>`_), and should contain
the following custom entry types:

.. example taken from tests/sourcedirs/bibgloss_sortkeys

**glossary term** (``name`` and ``description`` are required fields):

.. code-block:: bibtex

    @glsterm{gtkey1,
        name = {name},
        description = {full description \textbf{with latex}},
        plural = {some names},
        text = {alternative text},
        sort = {a},
        symbol = {\ensuremath{n}}
    }

**acronym** (``abbreviation`` and ``longname`` are required fields):

.. code-block:: bibtex

    @glsacronym{akey1,
        abbreviation = {MA},
        longname = {My Abbreviation},
        description = {full description},
        plural = {MAs},
        longplural = {Some Abbreviations}
    }

**symbol** (``name`` and ``description`` are required fields):

.. code-block:: bibtex

    @glssymbol{symbol1,
        name = {\ensuremath{\pi}},
        description = {full description},
        plural = {\ensuremath{\pi}s},
        text = {alternative text},
        sort = {sortkey}
    }

Alternatively, the glossary can be supplied as a TeX file:

.. code-block:: tex

    \newglossaryentry{gtkey1}{
        name={name},
        description={full description \textbf{with latex}}
        plural={names},
        text={alternative text},
        sort={a},
        symbol = {\ensuremath{n}}
        }
    \newacronym[plural={AAs}]{akey1}{AA}{An Abbreviation}
    \newglossaryentry{symbol1}{
        name={\ensuremath{\pi}},
        description={full description},
        plural={\ensuremath{\pi}s},
        text={alternative text},
        sort={b},
        type={symbols}
        }

.. note::

    To parse a glossary in TeX format, the
    `TexSoup <https://github.com/alvinwan/TexSoup>`_ package is required.

    ``newglossaryentry`` with ``type={symbols}`` are considered to be symbols,
    no other types are recognised.

.. attention::

    All labels and description text are converted from latex to rst
    by `Pandoc <https://pandoc.org/>`_, then rst to docutils,
    before being output to the final document.

    To skip this conversion (and only output as plain text) set
    the sphinx configuration variable ``bibgloss_convert_latex = False``

.. seealso::

    The `LaTeX/Glossary guide <https://en.wikibooks.org/wiki/LaTeX/Glossary>`_,
    for further description of each field.


Usage
-----

.. rst:role:: gls

    The ``gls`` role will output the 'name' or 'abbreviation' field of the entry:

    .. code-block:: rst

        :gls:`gtkey1`, :gls:`akey1`, :gls:`symbol1`

    :gls:`gtkey1`, :gls:`akey1`, :gls:`symbol1`

.. rst:role:: glspl

    The ``glspl`` role will output the 'plural' field of the entry,
    or (if not present) will append an 's' to the 'name' or 'abbreviation' field.

    .. code-block:: rst

        :glspl:`gtkey1`, :glspl:`akey1`, :glspl:`symbol1`

    :glspl:`gtkey1`, :glspl:`akey1`, :glspl:`symbol1`

.. rst:role:: glsc

    The ``glsc`` and ``glscpl`` capitalise the respective labels.

    .. code-block:: rst

        :glsc:`gtkey1`, :glscpl:`gtkey1`

    :glsc:`gtkey1`, :glscpl:`gtkey1`

.. rst:directive:: .. bibglossary:: path/to/glossary

    When creating the glossary, it is of note that, if the file extension is not
    given, then ``bibglossary`` will attempt to find the best match
    in the parent folder. The glossary will be sorted by lower case,
    'name'/'abbreviation' field, or 'sort' field (if it exists).

    .. code-block:: rst

        .. rubric:: Glossary

        .. bibglossary:: _static/example_glossary

    .. rubric:: Glossary

    .. bibglossary:: _static/example_glossary

    In order to use multiple glossaries, across one or more files, and avoid
    hyperlink clashes, it is possible to set a ``keyprefix`` to distinguish
    which glossary is being referenced.

    .. code-block:: rst

        :gls:`a-gtkey1`

        .. bibglossary:: _static/example_glossary
           :keyprefix: a-

    :gls:`a-gtkey1`

    .. bibglossary:: _static/example_glossary
       :keyprefix: a-

    Additional options include:

    - ``encoding`` to specify the encoding of the glossary file
    - ``unsorted`` to sort the glossary by order of first use (rather than alphanumerically)
    - ``all`` to output all glossary terms (including unused)

    .. code-block:: rst

        :gls:`b-akey1`

        .. bibglossary:: _static/example_glossary
           :encoding: utf8
           :unsorted:
           :keyprefix: b-

    :gls:`b-akey1`, :glsc:`b-gtkey1`

    .. bibglossary:: _static/example_glossary
        :encoding: utf8
        :unsorted:
        :keyprefix: b-

.. seealso::

    Additional options, known issues, and workarounds can be found in the
    `sphinxcontrib-bibtex <https://sphinxcontrib-bibtex.readthedocs.io>`_,
    documentation.

Python API
----------

The loading, conversion and storage of each glossary file is handled by a
:py:class:`~ipypublish.bib2glossary.classes.BibGlossDB` instance.

.. nbinput:: python
    :execution-count: 1

    from ipypublish.bib2glossary import BibGlossDB
    bibdb = BibGlossDB()
    bibdb.load("_static/example_glossary")
    len(bibdb)

.. nboutput::
    :execution-count: 1

    3

This class is a subclass of :py:class:`collections.abc.MutableMapping`,
and so can be used as a dictionary.

.. nbinput:: python
    :execution-count: 2

    print("gtkey1" in bibdb)
    entry = bibdb["gtkey1"]
    entry

.. nboutput::
    :execution-count: 2

    True
    BibGlossEntry(key=gtkey1,label=name)

Entries have attributes for the main fields, and can output to latex.

.. nbinput:: python
    :execution-count: 3

    print(entry.key)
    print(entry.label)
    print(entry.plural)
    print(entry.to_latex())

.. nboutput::
    :execution-count: 3

    gtkey1
    name
    some names
    \newglossaryentry{gtkey1}{
        description={full description \textbf{with latex}},
        name={name},
        plural={some names},
        sort={a},
        symbol={\ensuremath{n}},
        text={alternative text}
    }
