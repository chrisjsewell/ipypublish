""" a panflute filter to find raw elements
and convert them to format agnostic Span elements
"""
import re
from typing import Union  # noqa: F401
from panflute import Element, Doc, Cite, RawInline, Link  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.definitions import (
    ATTRIBUTE_CITE_CLASS, PREFIX_MAP, PREFIX_MAP_LATEX_R, PREFIX_MAP_RST_R,
    RST_KNOWN_ROLES, RAWSPAN_CLASS, RAWDIV_CLASS,
    CONVERTED_CITE_CLASS, CONVERTED_OTHER_CLASS, CONVERTED_DIRECTIVE_CLASS
)
from ipypublish.filters_pandoc.utils import (
    get_panflute_containers, get_pf_content_attr)


def create_cite_span(identifiers, rawformat, is_block,
                     prefix="", alt=None):
    """create a cite element from an identifier """
    citations = [pf.Citation(
        identifier
    ) for identifier in identifiers]
    pmapping = dict(dict(PREFIX_MAP)[prefix])
    classes = list(pmapping["classes"])
    classes += [RAWSPAN_CLASS, CONVERTED_CITE_CLASS, ATTRIBUTE_CITE_CLASS]
    attributes = dict(pmapping["attributes"])
    attributes["raw-format"] = rawformat
    if alt is not None:
        attributes["alt"] = str(alt)
    cite = Cite(citations=citations)
    span = pf.Span(
        cite,
        classes=classes,
        attributes=attributes
    )
    if is_block:
        return pf.Plain(span)
    else:
        return span


def process_internal_links(link, doc):
    # type: (Link, Doc) -> Element
    """extract links that point to internal items, e.g. [text](#label)"""
    if not isinstance(link, pf.Link):
        return None
    match = re.match(r'#(.+)$', link.url)
    if not match:
        return None

    return create_cite_span(
        [match.group(1)], "markdown", False,
        prefix=dict(PREFIX_MAP_LATEX_R).get("cref"),
        alt=pf.stringify(pf.Plain(*list(link.content))).strip())


def process_html_cites(container, doc):
    # type: (pf.Block, Doc) -> Element
    """extract raw html <cite data-cite="cite_key">text</cite>"""
    # if not (isinstance(block, get_panflute_containers(pf.RawInline))
    #         or isinstance(block, get_panflute_containers(pf.RawBlock))):
    #     return None
    content_attr = get_pf_content_attr(container, pf.RawInline)
    if not content_attr:
        content_attr = get_pf_content_attr(container, pf.RawBlock)

    if not content_attr:
        return None
    initial_content = getattr(container, content_attr)

    if not initial_content:
        return None

    new_content = []
    skip = 0

    for element in initial_content:

        if skip > 0:
            skip = skip - 1
            continue

        if not (isinstance(element, (pf.RawInline, pf.RawBlock)) and
                element.format in ("html", "html4", "html5")):
            new_content.append(element)
            continue

        match = re.match(
            r"<cite\s*data-cite\s*=\"?([^>\"]*)\"?>", element.text)
        if not match:
            new_content.append(element)
            continue

        # look for the closing tag
        span_content = []
        closing = element.next

        while closing:
            if (isinstance(closing, pf.RawInline) and
                    closing.format in ("html", "html5")):
                endmatch = re.match(r"^\s*</cite>\s*$", closing.text)
                if endmatch:
                    break
            span_content.append(closing)
            closing = closing.next

        if not closing:
            new_content.append(element)
            continue

        # TODO include original content
        new_content.append(create_cite_span([match.group(1)], "html",
                                            isinstance(element, pf.RawBlock)))
        skip = len(span_content) + 1

    setattr(container, content_attr, new_content)
    return container


def process_latex_raw(element, doc):
    # type: (Union[pf.RawInline, pf.RawBlock], pf.Doc) -> pf.Element
    """extract all latex adhering to \\tag{content} or \\tag[options]{content}
    to a Span element with class RAWSPAN_CLASS attributes:

    ::

        attributes={"format": "latex",
                    "tag": tag, "content": content, "options": options}

    - Cref, cref, ref, and cite will aslo have class CONVERTED_CITE_CLASS
    - everything else will also have class CONVERTED_OTHER_CLASS

    """
    if not (isinstance(element, (pf.RawInline, pf.RawBlock)) and
            element.format in ("tex", "latex")):
        return None

    return assess_latex(element.text, isinstance(element, pf.RawBlock))


def process_latex_str(block, doc):
    # type: (pf.Block, Doc) -> Union[pf.Block,None]
    """see process_latex_raw

    same but sometimes pandoc doesn't convert to a raw element
    """
    # TODO why is pandoc sometimes converting latex tags to Str?
    # >> echo "\cite{a}" | pandoc -f markdown -t json
    # {"blocks":[{"t":"Para","c":[{"t":"RawInline","c":["tex","\\cite{a}"]}]}],"pandoc-api-version":[1,17,5,4],"meta":{}}

    content_attr = get_pf_content_attr(block, pf.Str)
    if not content_attr:
        return None
    initial_content = getattr(block, content_attr)

    if not initial_content:
        return None

    new_content = []

    for element in initial_content:
        if not isinstance(element, pf.Str):
            new_content.append(element)
            continue
        for string in re.split(
            r"(\\[^\{\[]+\{[^\}]+\}|\\[^\{\[]+\[[^\]]*\]\{[^\}]+\})",
                element.text):
            if not string:
                continue
            new_element = assess_latex(string, False)
            if new_element is None:
                new_content.append(pf.Str(string))
            else:
                new_content.append(assess_latex(string, False))

    setattr(block, content_attr, new_content)
    return block


def assess_latex(text, is_block):
    """ test if text is a latex command
    ``\\tag{content}`` or ``\\tag[options]{content}``

    if so return a panflute.Span, with attributes:

    - format: "latex"
    - tag: <tag>
    - options: <options>
    - content: <content>
    - original: <full text>

    """
    # TODO these regexes do not match labels containing nested {} braces
    # use recursive regexes (https://stackoverflow.com/a/26386070/5033292)
    # with https://pypi.org/project/regex/

    # find tags with no option, i.e \tag{label}
    match_latex_noopts = re.match(
        r"^\s*\\([^\{\[]+)\{([^\}]+)\}\s*$", text)
    if match_latex_noopts:
        tag = match_latex_noopts.group(1)
        content = match_latex_noopts.group(2)
        if tag in dict(PREFIX_MAP_LATEX_R):
            new_element = create_cite_span(
                content.split(","), "latex", is_block,
                prefix=dict(PREFIX_MAP_LATEX_R).get(tag, ""))
            return new_element

        span = pf.Span(
            classes=[RAWSPAN_CLASS, CONVERTED_OTHER_CLASS],
            attributes={"format": "latex", "tag": tag,
                        "content": content, "original": text}
        )
        if is_block:
            return pf.Plain(span)
        else:
            return span

    # find tags with option, i.e \tag[options]{label}
    match_latex_wopts = re.match(
        r"^\s*\\([^\{\[]+)\[([^\]]*)\]\{([^\}]+)\}\s*$", text)
    if match_latex_wopts:
        tag = match_latex_wopts.group(1)
        options = match_latex_wopts.group(2)
        content = match_latex_wopts.group(3)

        span = pf.Span(
            classes=[RAWSPAN_CLASS, CONVERTED_OTHER_CLASS],
            attributes={"format": "latex",
                        "tag": tag,
                        "content": content,
                        "options": options,
                        "original": text}
        )
        if is_block:
            return pf.Plain(span)
        else:
            return span

    return None


def process_rst_roles(block, doc):
    # type: (pf.Block, Doc) -> Union[pf.Block,None]
    """extract rst adhering to ``:role:`label```, where role is a known
    to a Cite element with class RAWSPAN_CLASS and CONVERTED_CITE_CLASS
    and attributes:

    ::

        attributes={"format": "rst",
                    "role": tag, "content": content}

    """
    # "a :ref:`label` b" is converted to:
    # (Str(a) Space Str(:ref:) Code(label) Space Str(b))
    # if not (isinstance(block, get_panflute_containers(pf.Str))):
    #     return None
    content_attr = get_pf_content_attr(block, pf.Str)
    if not content_attr:
        return None
    initial_content = getattr(block, content_attr)

    if not initial_content:
        return None

    # match_rst_role = re.match(
    #     "^\\s*\\:([a-z]+)\\:\\`([^\\`]+)\\`$", element.text)

    new_content = []
    skip_next = False

    for element in initial_content:

        if skip_next:
            skip_next = False
            continue

        if not (isinstance(element, pf.Str)
                and isinstance(element.next, pf.Code)):
            new_content.append(element)
            continue

        if not (len(element.text) > 2 and
                element.text.startswith(":") and
                element.text.endswith(":")):
            new_content.append(element)
            continue

        role = element.text[1:-1]
        content = element.next.text

        if role in dict(PREFIX_MAP_RST_R):
            new_element = create_cite_span(
                content.split(","), "rst", False,
                prefix=dict(PREFIX_MAP_RST_R).get(role, ""))
            new_content.append(new_element)
            skip_next = True
        elif role in RST_KNOWN_ROLES:
            new_element = pf.Span(
                classes=[RAWSPAN_CLASS, CONVERTED_OTHER_CLASS],
                attributes={"format": "rst", "role": role,
                            "content": content,
                            "original": "{0}`{1}`".format(
                                element.text, element.next.text)
                            })
            new_content.append(new_element)
            skip_next = True
        else:
            new_content.append(element)

    # if len(new_content) != len(block.content):
    #     block.content = new_content
    #     return block
    setattr(block, content_attr, new_content)
    return block


def gather_processors(element, doc):
    """ we gather the processors,
    so that we don't have to do multiple passes
    """

    # apply processors that change one elements

    new_element = process_internal_links(element, doc)
    if new_element is not None:
        return new_element

    new_element = process_latex_raw(element, doc)
    if new_element is not None:
        return new_element

    # apply processors that change multiple inline elements in a block

    if (isinstance(element, get_panflute_containers(pf.Inline))
            or isinstance(pf.Table, pf.DefinitionItem)):

        new_element = process_html_cites(element, doc)
        if new_element is not None:
            element = new_element
        new_element = process_latex_str(element, doc)
        if new_element is not None:
            element = new_element
        new_element = process_rst_roles(element, doc)
        if new_element is not None:
            element = new_element

    # apply processors that change multiple block elements
    if isinstance(element, get_panflute_containers(pf.Block)):

        new_element = process_html_cites(element, doc)
        if new_element is not None:
            element = new_element

    return element


def wrap_rst_directives(doc):
    """search for rst directives and wrap them in divs

    with top line starting ``Str(..)Space()Str(name::)``, above a CodeBlock,
    and rst labels of the form ``Str(..)Space()Str(_name:)``

    """
    final_blocks = []
    skip_next = False
    for block in doc.content:

        if skip_next:
            skip_next = False
            continue

        if not isinstance(block, pf.Para):
            final_blocks.append(block)
            continue

        if len(block.content) < 3:
            final_blocks.append(block)
            continue

        if (isinstance(block.content[0], pf.Str)
            and block.content[0].text == ".."
                and isinstance(block.content[1], pf.Space)
                and isinstance(block.content[2], pf.Str)):

            if (len(block.content) == 3
                and block.content[2].text.startswith("_")
                    and block.content[2].text.endswith(":")):
                # the block is an rst label
                new_block = pf.Div(
                    block,
                    classes=[RAWDIV_CLASS, CONVERTED_OTHER_CLASS],
                    attributes={"format": "rst"}
                )
                final_blocks.append(new_block)
                continue

            if (block.content[2].text.endswith("::")
                    and isinstance(block.next, pf.CodeBlock)):
                # the block is a directive with body content
                # TODO at present we allow any directive name
                # the block may contain option directives, e.g. :width:
                skip_next = True

                inline_arg = ''
                if len(block.content) > 3:
                    inline_content = []
                    for el in block.content[3:]:
                        if isinstance(el, pf.SoftBreak):
                            break
                        inline_content.append(el)
                    if inline_content:
                        inline_arg = pf.stringify(
                            pf.Para(*inline_content)).replace("\n", "").strip()

                new_block = pf.Div(
                    block,
                    *pf.convert_text(block.next.text),
                    classes=[RAWDIV_CLASS, CONVERTED_DIRECTIVE_CLASS],
                    attributes={"format": "rst",
                                "directive": block.content[2].text[:-2],
                                "inline": inline_arg,
                                "has_body": True}
                )
                final_blocks.append(new_block)
                continue

            if (block.content[2].text.endswith("::")):
                # the block is a directive without body content
                # TODO at present we allow any directive name
                # the block may contain option directives, e.g. :width:

                inline_arg = ''
                if len(block.content) > 3:
                    inline_content = []
                    for el in block.content[3:]:
                        if isinstance(el, pf.SoftBreak):
                            break
                        inline_content.append(el)
                    if inline_content:
                        inline_arg = pf.stringify(
                            pf.Para(*inline_content)).replace("\n", "").strip()

                new_block = pf.Div(
                    block,
                    classes=[RAWDIV_CLASS, CONVERTED_DIRECTIVE_CLASS],
                    attributes={"format": "rst",
                                "directive": block.content[2].text[:-2],
                                "inline": inline_arg,
                                "has_body": False}
                )
                final_blocks.append(new_block)
                continue

        final_blocks.append(block)

    doc.content = final_blocks


def prepare(doc):
    # type: (Doc) -> None
    wrap_rst_directives(doc)


def finalize(doc):
    # type: (Doc) -> None
    pass


def main(doc=None, extract_formats=True):
    # type: (Doc, bool) -> None
    """if extract_formats then convert citations defined in
    latex, rst or html formats to special Span elements
    """
    return pf.run_filter(gather_processors,
                         prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
