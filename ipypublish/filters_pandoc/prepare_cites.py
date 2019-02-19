""" a panflute filter to find citations in markdown,
with attributes and prefixes,

- extract the attributes, classes and prefix
- wrap the cite with a Span with class 'attribute-Cite',
- add the classes, attributes and prefix to the Span, and
- remove the attribute string and prefix

For example:

```
+@label {}.class-name a=1} xyz *@label2* @label3{ .b}
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

meta["ipub"]["pandoc"]["at_notation"] = False

"""
from panflute import Element, Doc, Cite, RawInline, Link  # noqa: F401
import panflute as pf


from ipypublish.filters_pandoc.utils import (
    find_attributes, get_pf_content_attr)
from ipypublish.filters_pandoc.definitions import (
    ATTRIBUTE_CITE_CLASS, IPUB_META_ROUTE, PREFIX_MAP)


def process_citations(element, doc):
    # type: (Element, Doc) -> Element
    if not doc.get_metadata(IPUB_META_ROUTE + ".at_notation", True):
        return None

    content_attr = get_pf_content_attr(element, pf.Cite)
    if not content_attr:
        return None
    initial_content = getattr(element, content_attr)

    if not initial_content:
        return None

    final_content = []
    skip = 0
    for subel in initial_content:

        if skip:
            skip -= 1
            continue

        if not isinstance(subel, pf.Cite):
            final_content.append(subel)
            continue

        classes = []
        attributes = {}
        append = None

        # check if the cite has a valid prefix, if so extract it
        if (isinstance(subel.prev, pf.Str) and subel.prev.text
                and (subel.prev.text[-1] in dict(PREFIX_MAP))):

            prefix = subel.prev.text[-1]
            mapping = dict(dict(PREFIX_MAP)[prefix])
            classes.extend(mapping["classes"])
            attributes.update(mapping["attributes"])

            # remove prefix from preceding string
            string = final_content.pop()
            if len(string.text) > 1:
                final_content.append(pf.Str(string.text[:-1]))

        # check if the cite has a preceding class/attribute container
        attr_dict = find_attributes(subel, allow_space=True)
        if attr_dict:
            classes.extend(attr_dict["classes"])
            attributes.update(attr_dict["attributes"])
            skip = len(attr_dict["elements"])
            append = attr_dict["append"]

        if classes or attributes:
            classes.append(ATTRIBUTE_CITE_CLASS)
            final_content.append(pf.Span(subel,
                                         classes=sorted(set(classes)),
                                         attributes=attributes))
        else:
            final_content.append(subel)

        if append:
            final_content.append(append)

    setattr(element, content_attr, final_content)
    return element


def prepare(doc):
    # type: (Doc) -> None
    pass


def finalize(doc):
    # type: (Doc) -> None
    pass


def main(doc=None, extract_formats=True):
    # type: (Doc) -> None
    """if extract_formats then convert citations defined in
    latex, rst or html formats to special Span elements
    """
    return pf.run_filter(process_citations,
                         prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
