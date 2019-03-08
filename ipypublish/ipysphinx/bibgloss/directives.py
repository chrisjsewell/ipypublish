""" define the bibglossary directive
"""

import ast  # parse(), used for filter
import os.path  # getmtime()
import sphinx.util

from docutils.parsers.rst import Directive, directives
from sphinx.util.console import bold, standout

from ipypublish.bib2glossary.common import parse_bib, get_empty_bib
from ipypublish.ipysphinx.bibgloss.nodes import BibGlossaryNode
from ipypublish.ipysphinx.bibgloss.cache import BibliographyCache, BibfileCache


logger = sphinx.util.logging.getLogger(__name__)


def process_start_option(value):
    """Process and validate the start option value
    of a ``bibglossary`` directive.
    If *value* is ``continue`` then this function returns -1,
    otherwise *value* is converted into a positive integer.
    """
    if value == "continue":
        return -1
    else:
        return directives.positive_int(value)


class BibGlossaryDirective(Directive):

    """Class for processing the ``bibglossary`` directive.

    Parses the bibliography files, and produces a
    :class:`~ipypublish.ipysphinx.bibgloss.nodes.BibGlossaryNode` node.

    .. seealso::

       Further processing of the resulting
       :class:`~ipypublish.ipysphinx.bibgloss.nodes.BibGlossaryNode`
       node is done by
       :class:`~ipypublish.ipysphinx.bibgloss.transforms.BibGlossaryTransform`.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False
    option_spec = {
        'cited': directives.flag,
        'notcited': directives.flag,
        'all': directives.flag,
        'filter': directives.unchanged,
        # 'style': directives.unchanged,
        # 'list': directives.unchanged,
        'enumtype': directives.unchanged,
        'start': process_start_option,
        'encoding': directives.encoding,
        'labelprefix': directives.unchanged,
        'keyprefix': directives.unchanged,
    }

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

        bibcache = BibliographyCache(
            list_="citation",  # self.options.get("list", "citation"),
            enumtype=self.options.get("enumtype", "arabic"),
            start=self.options.get("start", 1),
            # style=self.options.get(
            #     "style", env.app.config.bibgloss_default_style),
            filter_=filter_,
            encoding=self.options.get(
                'encoding',
                self.state.document.settings.input_encoding),
            labelprefix=self.options.get("labelprefix", ""),
            keyprefix=self.options.get("keyprefix", ""),
            labels={},
            bibfiles=[],
        )
        if (bibcache.list_ not in set(["bullet", "enumerated", "citation"])):
            logger.warning(
                "unknown bibliography list type '{0}'.".format(bibcache.list_))
        for bibfile in self.arguments[0].split():
            # convert to normalized absolute path to ensure that the same file
            # only occurs once in the cache
            bibfile = os.path.normpath(env.relfn2path(bibfile.strip())[1])
            self.process_bibfile(bibfile, bibcache.encoding)
            env.note_dependency(bibfile)
            bibcache.bibfiles.append(bibfile)
        env.bibgloss_cache.set_bibliography_cache(env.docname, id_, bibcache)
        return [BibGlossaryNode('', ids=[id_])]

    def parse_bibfile(self, bibfile, encoding):
        """Parse *bibfile*, and return parsed data.

        :param bibfile: The bib file name.
        :type bibfile: ``str``
        :return: The parsed bibliography data.
        :rtype: :class:`bibtexparser.bibdatabase.BibDatabase`
        """
        logger.info(
            bold("parsing bibtex file {0}... ".format(bibfile)), nonl=True)
        bib = parse_bib(path=bibfile, encoding=encoding)
        logger.info("parsed {0} entries"
                    .format(len(bib.get_entry_dict())))
        return bib

    def update_bibfile_cache(self, bibfile, mtime, encoding):
        """Parse *bibfile* (see :meth:`parse_bibfile`), and store the
        parsed data, along with modification time *mtime*, in the
        bibtex cache.

        :param bibfile: The bib file name.
        :type bibfile: ``str``
        :param mtime: The bib file's modification time.
        :type mtime: ``float``
        :return: The parsed bibliography data.
        :rtype: :class:`bibtexparser.bibdatabase.BibDatabase`
        """
        data = self.parse_bibfile(bibfile, encoding)
        env = self.state.document.settings.env
        env.bibgloss_cache.bibfiles[bibfile] = BibfileCache(
            mtime=mtime,
            data=data)
        return data

    def process_bibfile(self, bibfile, encoding):
        """Check if ``env.bibgloss_cache.bibfiles[bibfile]`` is still
        up to date. If not, parse the *bibfile* (see
        :meth:`update_bibfile_cache`), and store parsed data in the
        bibtex cache.

        :param bibfile: The bib file name.
        :type bibfile: ``str``
        :return: The parsed bibliography data.
        :rtype: :class:`bibtexparser.bibdatabase.BibDatabase`
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
                mtime=-float("inf"), data=get_empty_bib())
            return cache[bibfile].data
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
        return cache[bibfile].data
