# -*- coding: utf-8 -*-
"""
caching of the bibglossaries

Originally adapted from: https://github.com/mcmtroffaes/sphinxcontrib-bibtex
"""

import six
try:                 # pragma: no cover
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict
import ast
import collections
import copy
from ordered_set import OrderedSet
import re


def _raise_invalid_node(node):
    """Helper method to raise an exception when an invalid node is
    visited.
    """
    raise ValueError("invalid node %s in filter expression" % node)


class _FilterVisitor(ast.NodeVisitor):

    """Visit the abstract syntax tree of a parsed filter expression."""

    entry = None
    """The bibliographic entry to which the filter must be applied."""

    cited_docnames = False
    """The documents where the entry is cited (empty if not cited)."""

    def __init__(self, entry, docname, cited_docnames):
        self.entry = entry
        self.docname = docname
        self.cited_docnames = cited_docnames

    def visit_Module(self, node):  # noqa: N802
        if len(node.body) != 1:
            raise ValueError(
                "filter expression cannot contain multiple expressions")
        return self.visit(node.body[0])

    def visit_Expr(self, node):  # noqa: N802
        return self.visit(node.value)

    def visit_BoolOp(self, node):  # noqa: N802
        outcomes = (self.visit(value) for value in node.values)
        if isinstance(node.op, ast.And):
            return all(outcomes)
        elif isinstance(node.op, ast.Or):
            return any(outcomes)
        else:  # pragma: no cover
            # there are no other boolean operators
            # so this code should never execute
            assert False, "unexpected boolean operator %s" % node.op

    def visit_UnaryOp(self, node):  # noqa: N802
        if isinstance(node.op, ast.Not):
            return not self.visit(node.operand)
        else:
            _raise_invalid_node(node)

    def visit_BinOp(self, node):  # noqa: N802
        left = self.visit(node.left)
        op = node.op
        right = self.visit(node.right)
        if isinstance(op, ast.Mod):
            # modulo operator is used for regular expression matching
            if not isinstance(left, six.string_types):
                raise ValueError(
                    "expected a string on left side of %s" % node.op)
            if not isinstance(right, six.string_types):
                raise ValueError(
                    "expected a string on right side of %s" % node.op)
            return re.search(right, left, re.IGNORECASE)
        elif isinstance(op, ast.BitOr):
            return left | right
        elif isinstance(op, ast.BitAnd):
            return left & right
        else:
            _raise_invalid_node(node)

    def visit_Compare(self, node):  # noqa: N802
        # keep it simple: binary comparators only
        if len(node.ops) != 1:
            raise ValueError("syntax for multiple comparators not supported")
        left = self.visit(node.left)
        op = node.ops[0]
        right = self.visit(node.comparators[0])
        if isinstance(op, ast.Eq):
            return left == right
        elif isinstance(op, ast.NotEq):
            return left != right
        elif isinstance(op, ast.Lt):
            return left < right
        elif isinstance(op, ast.LtE):
            return left <= right
        elif isinstance(op, ast.Gt):
            return left > right
        elif isinstance(op, ast.GtE):
            return left >= right
        elif isinstance(op, ast.In):
            return left in right
        elif isinstance(op, ast.NotIn):
            return left not in right
        else:
            # not used currently: ast.Is | ast.IsNot
            _raise_invalid_node(op)

    def visit_Name(self, node):  # noqa: N802
        """Calculate the value of the given identifier."""
        id_ = node.id
        if id_ == 'type':
            return self.entry.type.lower()
        elif id_ == 'key':
            return self.entry.key.lower()
        elif id_ == 'cited':
            return bool(self.cited_docnames)
        elif id_ == 'docname':
            return self.docname
        elif id_ == 'docnames':
            return self.cited_docnames
        elif id_ == 'True':
            return True
        elif id_ == 'False':
            return False
        else:
            return self.entry.get(id_, "")

    def visit_Set(self, node):  # noqa: N802
        return frozenset(self.visit(elt) for elt in node.elts)

    def visit_Str(self, node):  # noqa: N802
        return node.s

    # NameConstant is Python 3.4 only so do not insist on coverage
    def visit_NameConstant(self, node):  # noqa: N802
        return node.value

    def generic_visit(self, node):
        _raise_invalid_node(node)


class Cache:

    """Global bibgloss extension information cache. Stored in
    ``app.env.bibgloss_cache``, so must be picklable.
    """

    bibfiles = None
    """A :class:`dict` mapping .bib file names (relative to the top
    source folder) to :class:`BibfileCache` instances.
    """

    _bibliographies = None
    """Each bibglossary directive is assigned an id of the form
    bibtex-bibglossary-xxx. This :class:`dict` maps each docname
    to another :class:`dict` which maps each id
    to information about the bibliography directive,
    :class:`BibliographyCache`. We need to store this extra
    information separately because it cannot be stored in the
    :class:`~ipypublish.sphinx.gls.nodes.BibGlossaryNode` nodes
    themselves.
    """

    _cited = None
    """A :class:`dict` mapping each docname to a :class:`set` of
    citation keys.
    """

    _enum_count = None
    """A :class:`dict` mapping each docname to an :class:`int`
    representing the current bibliography enumeration counter.
    """

    def __init__(self):

        self.bibfiles = {}
        self._bibliographies = collections.defaultdict(dict)
        self._cited = collections.defaultdict(OrderedSet)
        self._enum_count = {}

    def purge(self, docname):
        """Remove  all information related to *docname*.

        :param docname: The document name.
        :type docname: :class:`str`
        """
        self._bibliographies.pop(docname, None)
        self._cited.pop(docname, None)
        self._enum_count.pop(docname, None)

    def inc_enum_count(self, docname):
        """Increment enumeration list counter for document *docname*."""
        self._enum_count[docname] += 1

    def set_enum_count(self, docname, value):
        """Set enumeration list counter for document *docname* to *value*."""
        self._enum_count[docname] = value

    def get_enum_count(self, docname):
        """Get enumeration list counter for document *docname*."""
        return self._enum_count[docname]

    def add_cited(self, key, docname):
        """Add the given *key* to the set of cited keys for
        *docname*.

        :param key: The citation key.
        :type key: :class:`str`
        :param docname: The document name.
        :type docname: :class:`str`
        """
        self._cited[docname].add(key)

    def get_cited_docnames(self, key):
        """Return the *docnames* from which the given *key* is cited.

        :param key: The citation key.
        :type key: :class:`str`
        """
        return frozenset([
            docname for docname, keys in six.iteritems(self._cited)
            if key in keys])

    def get_label_from_key(self, key):
        """Return label for the given key."""
        for bibcache in self.get_all_bibliography_caches():
            if key in bibcache.labels:
                return bibcache.labels[key]
        else:
            raise KeyError("%s not found" % key)

    def get_plural_from_key(self, key):
        """Return label for the given key."""
        for bibcache in self.get_all_bibliography_caches():
            if key in bibcache.plurals:
                return bibcache.plurals[key]
        else:
            raise KeyError("%s not found" % key)

    def get_all_cited_keys(self):
        """Yield all citation keys, sorted first by document
        (alphabetical), then by citation order in the document.
        """
        for docname in sorted(self._cited):
            for key in self._cited[docname]:
                yield key

    def set_bibliography_cache(self, docname, id_, bibcache):
        """Register *bibcache* (:class:`BibliographyCache`)
        with id *id_* for document *docname*.
        """
        assert id_ not in self._bibliographies[docname]
        self._bibliographies[docname][id_] = bibcache

    def get_bibliography_cache(self, docname, id_):
        """Return :class:`BibliographyCache` with id *id_* in
        document *docname*.
        """
        return self._bibliographies[docname][id_]

    def get_all_bibliography_caches(self):
        """Return all bibliography caches."""
        for bibcaches in six.itervalues(self._bibliographies):
            for bibcache in six.itervalues(bibcaches):
                yield bibcache

    def _get_bibliography_entries(self, docname, id_, warn):
        """Return filtered bibliography entries, sorted by occurence
        in the bib file.
        """
        # get the information of this bibliography node
        bibcache = self.get_bibliography_cache(docname=docname, id_=id_)
        # generate entries
        for bibfile in bibcache.bibfiles:
            for entry in self.bibfiles[bibfile].data.values():
                # beware: the prefix is not stored in the data
                # to allow reusing the data for multiple bibliographies
                cited_docnames = self.get_cited_docnames(
                    bibcache.keyprefix + entry.key)
                visitor = _FilterVisitor(
                    entry=entry,
                    docname=docname,
                    cited_docnames=cited_docnames)
                try:
                    success = visitor.visit(bibcache.filter_)
                except ValueError as err:
                    warn("syntax error in :filter: expression; %s" % err)
                    # recover by falling back to the default
                    success = bool(cited_docnames)
                if success:
                    # entries are modified in an unpickable way
                    # when formatting, so fetch a deep copy
                    # and return this copy with prefixed key
                    # we do not deep copy entry.collection because that
                    # consumes enormous amounts of memory
                    # entry.collection = None
                    entry2 = copy.deepcopy(entry)
                    entry2.key = bibcache.keyprefix + entry.key
                    yield entry2

    def get_bibliography_entries(self, docname, id_, warn):
        """Return filtered bibliography entries, sorted by citation order."""
        # get entries, ordered by bib file occurrence
        entries = OrderedDict(
            (entry.key, entry) for entry in
            self._get_bibliography_entries(
                docname=docname, id_=id_, warn=warn))
        # order entries according to which were cited first
        # first, we add all keys that were cited
        # then, we add all remaining keys
        sorted_entries = []
        for key in self.get_all_cited_keys():
            try:
                entry = entries.pop(key)
            except KeyError:
                pass
            else:
                sorted_entries.append(entry)
        sorted_entries += six.itervalues(entries)
        return sorted_entries


class BibfileCache(collections.namedtuple('BibfileCache', 'mtime data')):

    """Contains information about a parsed .bib file.

    .. attribute:: mtime

        A :class:`float` representing the modification time of the .bib
        file when it was last parsed.

    .. attribute:: data

        A ipypublish.bib2glossary.BibGlossDB instance

    """


class BibliographyCache(collections.namedtuple(
    'BibliographyCache',
    """bibfiles encoding style unsorted labels plurals filter_ keyprefix
""")):

    """Contains information about a bibliography directive.

    .. attribute:: bibfiles

        A :class:`list` of :class:`str`\\ s containing the .bib file
        names (relative to the top source folder) that contain the
        references.

    .. attribute:: encoding

        The encoding of the glossary file.

    .. attribute:: style

        The glossary style.

    .. attribute:: unsorted

        If True the glossary terms will be sorted by order of use,
        rather than alphabetically

    .. attribute:: labels

        Maps citation keys to their final labels.

    .. attribute:: plurals

        Maps citation keys to their final pluralised labels.

    .. attribute:: keyprefix

        This bibliography's string prefix for citation keys.

    .. attribute:: filter_

        An :class:`ast.AST` node, containing the parsed filter expression.
    """
