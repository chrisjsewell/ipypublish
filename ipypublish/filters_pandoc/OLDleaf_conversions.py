""" a panflute filter to perform format conversions
on elements with no children,
such as converting between rst roles and latex tags

"""
import re

from panflute import Element, Doc, Table, Inline  # noqa: F401
import panflute as pf


def latex_to_rst(element, doc):
    # type: (Element, Doc) -> None
    """attempt to replace latex tags with rst directives

    Supported: cref, Cref, ref, cite, todo

    If meta["ipub"][use_numref"] = True,
    then cref will be replaced with numref directive instead of ref

    """

    if not doc.format == "rst":
        return None

    if not (isinstance(element, (pf.RawInline, pf.RawBlock)) and
            element.format in ["tex", "latex"]):
        return None

    use_numref = doc.get_metadata("ipub.use_numref", False)
    ref_role = "numref" if use_numref else "ref"

    # find tags with no option, i.e \tag{label}
    match_noopts = re.match(
        r"^\s*\\([^\{\[]+)\{([^\}]+)\}\s*$", element.text)

    if match_noopts:
        tag = match_noopts.group(1)
        label = match_noopts.group(2)
        rst_dir = {"cref": ":{numref}:`{label}`",
                   "Cref": ":{numref}:`{label}`",
                   "ref": ":ref:`{label}`",
                   "cite": " :cite:`{label}` ",
                   "todo": "\n\n.. todo:: {label}\n\n",
                   }.get(tag, None)
        if rst_dir and isinstance(element, pf.RawInline):
            return pf.RawInline(
                rst_dir.format(label=label, numref=ref_role), format='rst')
        if rst_dir and isinstance(element, pf.RawBlock):
            return pf.RawBlock(
                rst_dir.format(label=label, numref=ref_role), format='rst')

    # find tags with option, i.e \tag[options]{label}
    match_wopts = re.match(
        r"^\s*\\([^\{\[]+)\[([^\]]*)\]\{([^\}]+)\}\s*$", element.text)

    if match_wopts:
        tag = match_wopts.group(1)
        options = match_wopts.group(2)
        label = match_wopts.group(3)
        rst_dir = {
            "todo": "\n\n.. todo:: {label}\n\n",
        }.get(tag, None)
        if rst_dir and isinstance(element, pf.RawInline):
            return pf.RawInline(
                rst_dir.format(label=label, options=options), format='rst')
        if rst_dir and isinstance(element, pf.RawBlock):
            return pf.RawBlock(
                rst_dir.format(label=label, options=options), format='rst')


def latex_to_html(element, doc):
    # type: (Element, Doc) -> None
    """attempt to replace latex tags with html tags"""

    if doc.format not in ("html", "html5"):
        return None

    # TODO latex_to_html


# now handled by prepare cite elements and format cite
def mkdown_to_latex(element, doc):
    # type: (Element, Doc) -> None
    """if links begin with `#`, use \\ref instead of \\hyperlink,
    if citation @label use \\cref{label} (or tag of metadata("ipub.reftag"))

    """
    if doc.format not in ("latex", "tex"):
        return None

    prefix = ""
    reftag = doc.get_metadata("ipub.reftag", "cref")

    if isinstance(element, pf.Link):
        element = element  # type: pf.Link

        if re.match(r'#(.+)$', element.url):
            label = re.match(r'#(.+)$', element.url).group(1)
            # TODO sanitize label or test it is correct format?
            # TODO if at start of sentence, use Cref
            return pf.RawInline(
                '{0}\\{1}{{{2}}}'.format(prefix, reftag, label),
                format='tex')

    if isinstance(element, pf.Cite):
        return pf.RawInline("\\{0}{{{1}}}".format(
            reftag,
            ",".join([c.id for c in element.citations])), format="tex")


# now handled by prepare cite elements
def mkdown_to_rst(element, doc):
    # type: (Element, Doc) -> None
    """if links begin with `#`, use :ref: instead of hyperlink
    if citation @label use :ref:`label`
    (or numref if metadata("ipub.use_numref"))

    """

    if doc.format != "rst":
        return None

    ref_role = doc.get_metadata("ipub.use_numref", "ref")

    if isinstance(element, pf.Link):
        element = element  # type: pf.Link

        if re.match(r'#(.+)$', element.url):
            label = re.match(r'#(.+)$', element.url).group(1)
            # TODO sanitize label or test it is correct format?
            return pf.RawInline(
                ":{0}:`{1}`".format(ref_role, label),
                format='rst')

    # now handled by format cite elements
    if isinstance(element, pf.Cite):
        return [
            pf.RawInline(
                ":{0}:`{1}`".format(ref_role, c.id),
                format='rst') for c in element.citations
        ]


#  now handled by prepare cite elements
def html_data_cite(element, doc):
    # type: (Element, Doc) -> None
    """ replace html style citations; <cite data-cite="cite_key">text</cite>

    """
    if doc.format not in ("latex", "tex", "rst"):
        return None

    if (isinstance(element, pf.RawInline) and
            element.format in ("html", "html5")):
        match = re.match(
            r"<cite\s*data-cite\s*=\"?([^>\"]*)\"?>", element.text)
        if match:
            # look for the closing tag
            closing = element.next

            while closing:
                if (isinstance(element, pf.RawInline) and
                        element.format in ("html", "html5")):
                    endmatch = re.match(r"^\s*</cite>\s*$", closing.text)
                    if endmatch:
                        break
                closing = closing.next

            if closing:
                label = match.group(1)
                if doc.format in ("latex", "tex"):
                    new_content = pf.RawInline(
                        "\\cite{{{0}}}".format(label), format="tex")
                elif doc.format == "rst":
                    new_content = pf.RawInline(
                        " :cite:`{0}` ".format(label), format="rst")
                    # NB :cite: must have space at either side to be resolved
                else:
                    raise TypeError("wrong format: {}".format(doc.format))

                # traverse left and right, to find surrounding content
                init_content = []
                prev = element.prev
                while prev:
                    init_content.insert(0, prev)
                    prev = prev.prev
                final_content = []
                final = closing.next
                while final:
                    final_content.append(final)
                    final = final.next

                final_block = (
                    init_content + [new_content] + final_content)

                # element.parent.content = final_block
                # TODO see sergiocorreia/panflute#96
                # TODO this won't work if there are multiple substitutions in same block
                doc.to_replace[element.parent] = final_block


def replace_elements(element, doc):
    # type: (Element, Doc) -> None
    if element in doc.to_replace:
        return element.__class__(*doc.to_replace[element])


def rst_to_latex(element, doc):
    # type: (Element, Doc) -> None
    """attempt to replace rst directives with latex tags"""

    if not doc.format == "latex":
        return None

    # TODO rst_to_latex


def prepare(doc):
    # type: (Doc) -> None
    doc.to_replace = {}


def finalize(doc):
    # type: (Doc) -> None
    del doc.to_replace


def main(doc=None):
    # type: (Doc) -> None
    return pf.run_filters([latex_to_rst, rst_to_latex,
                           latex_to_html, mkdown_to_latex, mkdown_to_rst,
                           html_data_cite,
                           replace_elements],
                          prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
