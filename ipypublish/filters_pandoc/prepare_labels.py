""" a panflute filter to prepare document labelling in markdown files:

1) Add a ``$$reference`` key to the Document metadata

Then, for each Image, Math and Table found;

2) Extract labels and attributes to the right of Math or Table captions,
in the form; ``{#id .class-name a="an attribute"}``

3) If attributes found, remove them from the document and wrap the associated
   Math/Table in a Span/Div with the attributes and an additional class:
   ``labelled-Math`` or ``labelled-Table``

4) For all labelled Tables, Math and Images,
   place in metadata as e.g.
   meta["$$references"][label] = {"type": "Math", "number": 1}

For example:

    '$$a=1$$ {#a b=$2$}'


would be converted to this html:

.. code-block:: html

   <p>
   <span id="a" class="labelled-Math" data-b="2">
   <span class="math inline"><em>a</em> = 1</span>
   </span>
   </p>

"""
from panflute import Element, Doc, Table, Inline  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.utils import (
    compare_version, get_panflute_containers, find_attributes)

LABELLED_IMAGE_CLASS = "labelled-Image"
LABELLED_MATH_CLASS = "labelled-Math"
LABELLED_TABLE_CLASS = "labelled-Table"

REFTYPE_TABLE = "Table"
REFTYPE_IMAGE = "Image"
REFTYPE_MATH = "Math"


def resolve_tables(element, doc):
    # type: (Table, Doc) -> None
    if not isinstance(element, (pf.Table)):
        return None

    ref_type = REFTYPE_TABLE

    attributes = None
    if element.caption:  # type: Inline
        # attributes = _find_attribute(element.caption[0],
        #                              allow_any=True, delete_preceding=False)
        attributes = find_attributes(
            element.caption[-1], search_left=True, include_element=True)

    if not attributes:
        return None

    # update count
    doc.refcount[ref_type] += 1
    # add to metadata
    doc.metadata[
        "$$references"][attributes["id"]] = pf.MetaMap(**{
            "type": pf.MetaString(ref_type),
            "number": doc.refcount[ref_type]
        })
    # remove attribute from caption
    element.caption = [el for el in element.caption
                       if el not in attributes["elements"]]

    # wrap in a div
    return pf.Div(element,
                  classes=[
                      "labelled-{}".format(ref_type)] + attributes["classes"],
                  attributes=attributes["attributes"],
                  identifier=attributes["id"])


def resolve_equations_images(element, doc):
    # type: (Element, Doc) -> None

    # attribute equations in table captions / definition items?
    if not isinstance(element, get_panflute_containers(pf.Math)):
        return None

    if not element.content:
        return None

    to_delete = set()
    to_wrap = dict()

    subel = element.content[0]

    while subel:  # type: Element

        ref_type = None
        if isinstance(subel, pf.Math):
            ref_type = REFTYPE_MATH
        # elif isinstance(subel, pf.Table):
        #     ref_type = "Table"
        elif isinstance(subel, pf.Image):
            ref_type = REFTYPE_IMAGE
        else:
            subel = subel.next
            continue

        if isinstance(subel, pf.Image) and compare_version('1.16', '>='):
            # pandoc >= 1.16 already supports this
            # TODO for pandoc < 1.16 also look for attributes attached,
            # to the image path, as occurs with image references
            # see https://github.com/tomduck/pandoc-fignos/issues/14
            attributes = {
                "id": subel.identifier,
                # "classes": subel.classes,
                # "attributes": subel.attributes,
                "elements": []
            }

        else:
            attributes = find_attributes(subel)
            if attributes:
                to_wrap[subel] = attributes
                for _ in attributes["elements"]:
                    subel = subel.next

        if attributes and attributes["id"]:
            # update count
            doc.refcount[ref_type] += 1
            # add to metadata
            doc.metadata[
                "$$references"][attributes["id"]] = pf.MetaMap(**{
                    "type": pf.MetaString(ref_type),
                    "number": doc.refcount[ref_type]
                })

            to_delete.update(attributes["elements"])

        subel = subel.next

    new_content = [
        pf.Span(el,
                classes=[
                    "labelled-{}".format(ref_type)] + to_wrap[el]["classes"],
                attributes=to_wrap[el]["attributes"],
                identifier=to_wrap[el]["id"]
                )
        if el in to_wrap else el
        for el in element.content
        if el not in to_delete]

    # if isinstance(element, pf.Plain):
    #     return pf.Plain(*new_content)
    # else:
    #     return pf.Para(*new_content)
    element.content = new_content
    return element


def prepare(doc):
    # type: (Doc) -> None
    doc.refcount = {
        "Table": 0,
        "Image": 0,
        "Math": 0
    }
    doc.metadata["$$references"] = pf.MetaMap()


def finalize(doc):
    # type: (Doc) -> None
    del doc.refcount


def main(doc=None):
    # type: (Doc) -> None
    return pf.run_filters([resolve_tables, resolve_equations_images],
                          prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
