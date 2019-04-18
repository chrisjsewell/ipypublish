""" define the bibglossary directive

Originally adapted from: https://github.com/mcmtroffaes/sphinxcontrib-bibtex
"""

import ast  # parse(), used for filter
import os.path  # getmtime()
import sphinx.util

from docutils.parsers.rst import Directive, directives
from sphinx.util.console import bold, standout

from ipypublish.bib2glossary import BibGlossDB
from ipypublish.sphinx.gls.nodes import BibGlossaryNode
from ipypublish.sphinx.gls.cache import BibliographyCache, BibfileCache


logger = sphinx.util.logging.getLogger(__name__)


class BibGlossaryDirective(Directive):

    """Class for processing the ``bibglossary`` directive.

    Parses the bibliography files, and produces a
    :class:`~ipypublish.sphinx.gls.nodes.BibGlossaryNode` node.

    .. seealso::

       Further processing of the resulting
       :class:`~ipypublish.sphinx.gls.nodes.BibGlossaryNode`
       node is done by
       :class:`~ipypublish.sphinx.gls.transforms.BibGlossaryTransform`.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    option_spec = {
        'cited': directives.flag,
        'notcited': directives.flag,
        'all': directives.flag,
        'unsorted': directives.flag,
        'filter': directives.unchanged,
        'style': directives.unchanged,
        'encoding': directives.encoding,
        'keyprefix': directives.unchanged,
    }

    _allowed_styles = (
        "list"
    )
    _default_style = "list"

    def run(self):
        """Process .bib files, set file dependencies, and create a
        node that is to be transformed to the entries of the
        glossary.
        """
        env = self.state.document.settings.env
        # create id and cache for this node
        # this id will be stored with the node
        # and is used to look up additional data in env.bibgloss_cache
        # (implementation note: new_serialno only guarantees unique
        # ids within a single document, but we need the id to be
        # unique across all documents, so we also include the docname
        # in the id)
        id_ = 'bibtex-bibglossary-%s-%s' % (
            env.docname, env.new_serialno('bibgloss'))

        # set filter option
        if "filter" in self.options:
            if "all" in self.options:
                logger.warning(standout(":filter: overrides :all:"))
            if "notcited" in self.options:
                logger.warning(standout(":filter: overrides :notcited:"))
            if "cited" in self.options:
                logger.warning(standout(":filter: overrides :cited:"))
            try:
                filter_ = ast.parse(self.options["filter"])
            except SyntaxError:
                logger.warning(
                    standout("syntax error in :filter: expression") +
                    " (" + self.options["filter"] + "); "
                    "the option will be ignored"
                )
                filter_ = ast.parse("cited")
        elif "all" in self.options:
            filter_ = ast.parse("True")
        elif "notcited" in self.options:
            filter_ = ast.parse("not cited")
        else:
            # the default filter: include only cited entries
            filter_ = ast.parse("cited")

        style = self.options.get(
                "style", env.app.config.bibgloss_default_style)
        if style not in self._allowed_styles:
            logger.warning(
                "style '{}' not in allowed styles, defaulting to '{}'".format(
                    style, self._default_style
                ))
            style = self._default_style

        bibcache = BibliographyCache(
            style=style,
            unsorted=("unsorted" in self.options),
            filter_=filter_,
            encoding=self.options.get(
                'encoding',
                self.state.document.settings.input_encoding),
            keyprefix=self.options.get("keyprefix", ""),
            labels={},
            plurals={},
            bibfiles=[],
        )

        for bibfile in self.arguments[0].split():
            # convert to normalized absolute path to ensure that the same file
            # only occurs once in the cache
            bibfile = os.path.normpath(env.relfn2path(bibfile.strip())[1])
            # if the bibfile has been supplied with no extension, guess path
            bibfile = BibGlossDB().guess_path(bibfile) or bibfile
            self.process_bibfile(bibfile, bibcache.encoding)
            env.note_dependency(bibfile)
            bibcache.bibfiles.append(bibfile)
        env.bibgloss_cache.set_bibliography_cache(env.docname, id_, bibcache)
        return [BibGlossaryNode('', ids=[id_])]

    def update_bibfile_cache(self, bibfile, mtime, encoding):
        """Parse *bibfile*,  and store the
        parsed data, along with modification time *mtime*, in the
        bibtex cache.

        Parameters
        ----------
        bibfile: str
            The bib file name.
        mtime: float
            The bib file's modification time.

        """
        logger.info(
            bold("parsing bibtex file {0}... ".format(bibfile)), nonl=True)
        bibglossdb = BibGlossDB()
        bibglossdb.load(path=bibfile, encoding=encoding)
        logger.info("parsed {0} entries"
                    .format(len(bibglossdb)))
        env = self.state.document.settings.env
        env.bibgloss_cache.bibfiles[bibfile] = BibfileCache(
            mtime=mtime,
            data=bibglossdb)

    def process_bibfile(self, bibfile, encoding):
        """Check if ``env.bibgloss_cache.bibfiles[bibfile]`` is still
        up to date. If not, parse the *bibfile*, and store parsed data in the
        bibtex cache.

        Parameters
        ----------
        bibfile: str
            The bib file name.

        """
        env = self.state.document.settings.env
        cache = env.bibgloss_cache.bibfiles
        # get modification time of bibfile
        try:
            mtime = os.path.getmtime(bibfile)
        except OSError:
            logger.warning(
                standout("could not open bibtex file {0}.".format(bibfile)))
            cache[bibfile] = BibfileCache(  # dummy cache
                mtime=-float("inf"), data=BibGlossDB())
            return
        # get cache and check if it is still up to date
        # if it is not up to date, parse the bibtex file
        # and store it in the cache
        logger.info(
            bold("checking for {0} in bibtex cache... ".format(bibfile)),
            nonl=True)
        try:
            bibfile_cache = cache[bibfile]
        except KeyError:
            logger.info("not found")
            self.update_bibfile_cache(bibfile, mtime, encoding)
        else:
            if mtime != bibfile_cache.mtime:
                logger.info("out of date")
                self.update_bibfile_cache(bibfile, mtime, encoding)
            else:
                logger.info('up to date')
