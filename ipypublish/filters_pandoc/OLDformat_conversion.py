"""
pandoc filters which find elements from in format and convert them to another
"""
import re
from ipypublish.filters_pandoc.utils import ElementTypes as el
from ipypublish.filters_pandoc.utils import traverse_meta, sanitize_label

# TODO sphinx directives (like todo, warning etc...) to latex
# TODO latex_to_html


def latex2rst(key, value, fmt, meta):
    """attempt to replace latex tags with rst directives"""

    if fmt != "rst":
        return None

    use_numref, _ = traverse_meta(meta, ["ipub", "use_numref"],
                                  assert_type="MetaBool")
    numref = "numref" if use_numref else "ref"

    if ((key == 'RawInline' or key == 'RawBlock') and
            (value[0] == 'tex' or value[0] == 'latex')):

        match_noopts = re.match(
            r"^\s*\\([^\{\[]+)\{([^\}]+)\}\s*$", value[1])
        if match_noopts:
            tag = match_noopts.group(1)
            label = match_noopts.group(2)
            rst_dir = {"cref": ":{numref}:`{label}`",
                       "Cref": ":{numref}:`{label}`",
                       "ref": ":ref:`{label}`",
                       "cite": " :cite:`{label}` ",
                       "todo": "\n\n.. todo:: {label}\n\n",
                       }.get(tag, None)
            if rst_dir:
                if key == 'RawInline':
                    return el.RawInline(
                        'rst', rst_dir.format(label=label, numref=numref))
                else:
                    return el.RawBlock(
                        'rst', rst_dir.format(label=label, numref=numref))

        match_wopts = re.match(
            r"^\s*\\([^\{\[]+)\[([^\]]*)\]\{([^\}]+)\}\s*$", value[1])
        if match_wopts:
            tag = match_wopts.group(1)
            options = match_wopts.group(2)
            label = match_wopts.group(3)
            rst_dir = {
                "todo": "\n\n.. todo:: {label}\n\n",
            }.get(tag, None)
            if rst_dir:
                if key == 'RawInline':
                    return el.RawInline(
                        'rst',
                        rst_dir.format(label=label, options=options))
                else:
                    return el.RawBlock(
                        'rst',
                        rst_dir.format(label=label, options=options))


def resolve_references_filter(key, value, fmt, meta):
    """ identifies hyperlinks in the
    document and transforms them into valid LaTeX tags or rst directives
    calls so that linking to headers between cells is possible.

    if meta["ipub"]["at_notation"] = True, then
    interpret @label as a reference type based on its prefix modifier:

    - latex: '' = cite '+' = cref,    '^' = Cref,    '!' = ref,  '=' = eqref
    - rst: '' = :cite: '+' = :numref: '^' = :numref: '!' = :ref: '=' = :eq:

    also works with multi labels, e.g. ![@{ref1,ref2}]

    Parameters
    ----------
    key: str
        the type of the pandoc object (e.g. 'Str', 'Para')
    value:
        the contents of the object (e.g. a string for 'Str', a list of
        inline elements for 'Para')
    fmt: str
        is the target output format (as supplied by the
        `format` argument of `walk`)
    meta:
        is the document's metadata

    """
    use_at_notation, _ = traverse_meta(meta, ["ipub", "at_notation"],
                                       assert_type="MetaBool")
    use_numref, _ = traverse_meta(meta, ["ipub", "use_numref"],
                                  assert_type="MetaBool")
    reftag, _ = traverse_meta(meta, ["ipub", "reftag", 0],
                              assert_type="Str")
    prefix = ""

    # replace markdown references with latex ones
    if key == 'Link':
        target = value[-1][0]  # in older pandoc, no attributes at front
        m = re.match(r'#(.+)$', target)
        if m:
            # pandoc automatically makes labels for headings.
            label = sanitize_label(m.group(1))
            if fmt == "latex":
                return el.RawInline(
                    'tex', '{0}\\{1}{{{2}}}'.format(prefix, reftag, label))
            elif fmt == "rst":
                # RawInline('rst', ":ref:``".format(label))
                # TODO link vs ref?
                return None
            if fmt in ("html", "html5"):
                return None  # TODO

    # replace html style citations; <cite data-cite="cite_key"></cite>
    # TODO this does not remove any content between the start-end tags
    if key == 'RawInline' and value[0] == 'html':
        if re.match(r"^\s*</cite>\s*$", value[1]):
            return []  # remove
        match = re.match(
            r"<cite\s*data-cite\s*=\"?([^>\"]*)\"?>", value[1])
        if not match:
            return None
        key = match.group(1)
        if not key:
            return []
        if fmt == "latex":
            return el.RawInline('tex', "\\cite{{{0}}}".format(key))
        if fmt == "rst":
            return el.RawInline('rst', " :cite:`{0}` ".format(key))
            # NB citations must have space at either side to be resolved
        if fmt in ("html", "html5"):
                return None  # TODO

    # replace @label style references
    if use_at_notation:
        # References may occur in a variety of places; we must process them
        # all.
        if key in ['Para', 'Plain']:
            _process_at_refs(value, meta, fmt, use_numref)
        elif key == 'Image':
            _process_at_refs(value[-2], meta, fmt, use_numref)
        elif key == 'Table':
            _process_at_refs(value[-5], meta, fmt, use_numref)
        elif key == 'Span':
            _process_at_refs(value[-1], meta, fmt, use_numref)
        elif key == 'Emph':
            _process_at_refs(value, meta, fmt, use_numref)
        elif key == 'Strong':
            _process_at_refs(value, meta, fmt, use_numref)

    return None


def _process_at_refs(element, meta, fmt="latex", use_numref=True):
    """ find citation elements using @ notation
    and replace with appropriate latex tags / rst roles

    # NOTE in pandoc-xnos they repair_refs for
    # "-f markdown+autolink_bare_uris" with pandoc < 1.18
    """
    numref = "numref" if use_numref else "ref"

    deletions = []
    for i, sub_el in enumerate(element):
        if sub_el['t'] == 'Cite' and len(sub_el['c']) == 2:
            citations = sub_el['c'][0]
            # extracts the */+/! modifier in front of the Cite
            modifier = None
            if element[i-1]['t'] == 'Str':
                modifier = element[i - 1]['c'][-1]
                if modifier in ['^', '+', '!', '=']:
                    if len(element[i - 1]['c']) > 1:
                        # Cut the modifier off of the string
                        element[i-1]['c'] = element[i-1]['c'][:-1]
                    else:
                        # The element contains only the modifier; delete it
                        deletions.append(i-1)

            labels = [citation["citationId"] for citation in citations]

            if fmt == "latex":
                tag = {'+': 'cref', '^': "Cref", "!": "ref", "=": "eqref",
                       }.get(modifier, 'cite')
                if tag in ["ref", "eqref"] and len(citations) > 1:
                    tex = (
                        ", ".join(['\\{0}{{{1}}}'.format(tag, l)
                                   for l in labels[:-1]]) +
                        ' and \\{0}{{{1}}}'.format(tag, labels[-1]))
                else:
                    tex = '\\{0}{{{1}}}'.format(tag, ",".join(labels))

                element[i] = el.RawInline('tex', tex)

            if fmt == "rst":
                tag = {'+': numref, '^': numref, "!": "ref", "=": "eq",
                       }.get(modifier, 'cite')
                if tag == "cite":
                    rst = ' :{0}:`{1}` '.format(tag, ",".join(labels))
                    # NB citations must have space either side to be resolved
                elif len(citations) == 1:
                    rst = ':{0}:`{1}`'.format(tag, ",".join(labels))
                else:
                    rst = (
                        ",".join([':{0}:`{1}`'.format(tag, l)
                                  for l in labels[:-1]]) +
                        ' and :{0}:`{1}`'.format(tag, labels[-1]))

                element[i] = el.RawInline('rst', rst)

            if fmt in ("html", "html5"):
                return None  # TODO

    # delete in place
    deleted = 0
    for delete in deletions:
        del element[delete - deleted]
        deleted += 1
