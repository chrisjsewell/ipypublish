""" a panflute filter to find citations in markdown,
with attributes and prefixes,

- extract the attributes, classes and prefix
- wrap the cite with a Span with class 'attribute-Cite',
- add the classes, attributes and prefix to the Span, and
- remove the attribute string and prefix

For example:

```
+{@label .class-name a=1} xyz *@label2* {@label3 .b}
```

would be converted to this html:

```html
<p>
<span class="class-name attribute-Cite" data-a="1" data-prefix="+">
<span class="citation" data-cites="label">@label</span>
</span>
xyz
<em><span class="citation" data-cites="label2">@label2</span></em>
<span class="b attribute-Cite" data-prefix="{">
<span class="citation" data-cites="label3">@label3</span>
</span>
</p>
```

Optionally, this can be turned off by adding to the Document metadata

meta["ipub"]["at_notation"] = False

"""
from panflute import Element, Doc, Cite, RawInline, Link  # noqa: F401
import panflute as pf


from ipypublish.filters_pandoc.utils import process_attributes
from ipypublish.filters_pandoc.definitions import (
    ATTRIBUTE_CITE_CLASS, PREFIX_MAP_LATEX)


def find_attributes(element):
    # type: (Cite) -> (list, dict, list)
    classes = []
    attributes = {}
    delete_content = []

    # check if it is braced
    if isinstance(element.prev, pf.Str) and element.prev.text.endswith("{"):
        open_brace = element.prev
    else:
        open_brace = None

    # get classes and attributes of citation
    if open_brace:
        closing = False
        attr_content = []
        # find the closing brace
        neighbour = element.next
        # TODO respect brace in quote?
        while neighbour:
            # only allow certain elements within the attributes section
            # TODO document this requirement
            if not isinstance(neighbour, (pf.Str, pf.Space)):
                break
            if isinstance(neighbour, pf.Str) and "}" in neighbour.text:
                closing = True
                # make sure we only process attribute matter 
                # to the left of the brace, and that it is deleted
                brace_index = neighbour.text.find("}")
                if len(neighbour.text) == brace_index + 1:
                    attr_content.append(neighbour)
                    delete_content.extend(attr_content)
                else:
                    left_content = pf.Str(neighbour.text[:brace_index+1])
                    neighbour.text = neighbour.text[brace_index+1:]
                    delete_content.append(left_content)
                break
            attr_content.append(neighbour)
            neighbour = neighbour.next
        if closing:
            # extract classes and attributes from the attribute matter
            _attr_string = pf.stringify(pf.Plain(*delete_content),
                                        newlines=False)[:-1].strip()
            classes, attributes = process_attributes(_attr_string)

    # check for prefix and modify or delete its Str container
    if open_brace and len(open_brace.text) == 1:
        delete_content.append(open_brace)
    elif open_brace and len(open_brace.text) > 1:
        if open_brace.text[-2] in dict(PREFIX_MAP_LATEX).keys():
            attributes["prefix"] = open_brace.text[-2]
            if len(open_brace.text) == 2:
                delete_content.append(open_brace)
            else:
                open_brace.text = open_brace.text[:-2]
        else:
            open_brace.text = open_brace.text[:-1]
    elif isinstance(element.prev, pf.Str):
        if element.prev.text[-1] in dict(PREFIX_MAP_LATEX).keys():
            attributes["prefix"] = element.prev.text[-1]
            if len(element.prev.text) == 1:
                delete_content.append(element.prev)
            else:
                element.prev.text = element.prev.text[:-1]

    return classes, attributes, delete_content


def process_citations(element, doc):
    # type: (Cite, Doc) -> Element
    if not doc.get_metadata("ipub.at_notation", True):
        return None

    if not isinstance(element, pf.Cite):
        return None

    classes, attributes, delete_content = find_attributes(element)

    if delete_content:
        doc.to_delete.setdefault(element.parent, set()).update(delete_content)

    if attributes or classes:
        # wrap in a span
        classes.append(ATTRIBUTE_CITE_CLASS)
        return pf.Span(element,
                       classes=classes,
                       attributes=attributes)


def prepare(doc):
    # type: (Doc) -> None
    doc.to_delete = {}


def finalize(doc):
    # type: (Doc) -> None
    # TODO is this the best approach? see sergiocorreia/panflute#96
    for element, delete in doc.to_delete.items():
        if isinstance(element, pf.Table):
            element.caption = [e for e in element.caption if e not in delete]
        else:
            element.content = [e for e in element.content if e not in delete]
    del doc.to_delete


def main(doc=None, extract_formats=True):
    # type: (Doc) -> None
    """if extract_formats then convert citations defined in 
    latex, rst or html formats to special Span elements
    """
    return pf.run_filter(process_citations,
                         prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
