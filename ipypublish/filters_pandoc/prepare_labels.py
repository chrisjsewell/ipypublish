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

    '$a=1$ {#a b=$2$}'


would be converted to this html:

.. code-block:: html

   <p>
   <span id="a" class="labelled-Math" data-b="2">
   <span class="math inline"><em>a</em> = 1</span>
   </span>
   </p>

"""
import re
from panflute import Element, Doc, Table, Inline  # noqa: F401
import panflute as pf

from ipypublish.filters_pandoc.utils import (
    compare_version, process_attributes, get_panflute_containers)

LABELLED_IMAGE_CLASS = "labelled-Image"
LABELLED_MATH_CLASS = "labelled-Math"
LABELLED_TABLE_CLASS = "labelled-Table"

REFTYPE_TABLE = "Table"
REFTYPE_IMAGE = "Image"
REFTYPE_MATH = "Math"


def _find_attribute(start_el,
                    allow_space=True, allow_any=False, delete_preceding=True):
    # TODO allow_space should be optional per type
    # TODO should non-labelled attributes be allowed? i.e. {# .class a=1}

    adjacent = start_el
    attr_elements = []
    found_start = False
    found_end = False
    while adjacent:
        if (isinstance(adjacent, pf.Space) and (allow_space or allow_any)):
            if delete_preceding:
                attr_elements.append(adjacent)
            adjacent = adjacent.next
            continue
        elif (isinstance(adjacent, pf.Str)
              and re.match("^\\{\\#.+\\}$", adjacent.text)):
            found_start = True
            found_end = True
            attr_elements.append(adjacent)
            break
        elif (isinstance(adjacent, pf.Str)
              and re.match("^\\{\\#.+", adjacent.text)):
            found_start = True
            found_end = False
            attr_elements.append(adjacent)
            break
        elif not allow_any:
            break
        elif delete_preceding:
            attr_elements.append(adjacent)
        adjacent = adjacent.next

    if found_start and not found_end:
        adjacent = adjacent.next
        while adjacent:
            if (isinstance(adjacent, pf.Str)
                    and re.match(".*\\}$", adjacent.text)):
                found_end = True
                attr_elements.append(adjacent)
                break
            else:
                attr_elements.append(adjacent)
            adjacent = adjacent.next

    if not (found_start and found_end):
        return None

    string = pf.stringify(pf.Para(*attr_elements)
                          ).replace("\n", " ").strip()

    # split into the label and the rest
    # TODO does there always have to be a label?
    match = re.match("^\\{\\#([^\s]+)(.*)\\}$", string)
    label = match.group(1)
    classes, attributes = process_attributes(match.group(2))

    return {
        "label": label,
        "classes": classes,
        "attributes": attributes,
        "to_delete": attr_elements
    }


def resolve_tables(element, doc):
    # type: (Table, Doc) -> None
    if not isinstance(element, (pf.Table)):
        return None

    ref_type = REFTYPE_TABLE

    attributes = None
    if element.caption:  # type: Inline
        attributes = _find_attribute(element.caption[0],
                                     allow_any=True, delete_preceding=False)

    if not attributes:
        return None

    # update count
    doc.refcount[ref_type] += 1
    # add to metadata
    doc.metadata[
        "$$references"][attributes["label"]] = pf.MetaMap(**{
            "type": pf.MetaString(ref_type),
            "number": doc.refcount[ref_type]
        })
    # remove attribute from caption
    element.caption = [el for el in element.caption
                       if el not in attributes["to_delete"]]

    # wrap in a div
    return pf.Div(element,
                  classes=[
                      "labelled-{}".format(ref_type)] + attributes["classes"],
                  attributes=attributes["attributes"],
                  identifier=attributes["label"])


def resolve_equations_images(element, doc):
    # type: (Element, Doc) -> None

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
                "label": subel.identifier,
                # "classes": subel.classes,
                # "attributes": subel.attributes,
                "to_delete": []
            }
        else:
            attributes = _find_attribute(subel.next)
            if attributes:
                to_wrap[subel] = attributes
                for _ in attributes["to_delete"]:
                    subel = subel.next

        if attributes and attributes["label"]:
            # update count
            doc.refcount[ref_type] += 1
            # add to metadata
            doc.metadata[
                "$$references"][attributes["label"]] = pf.MetaMap(**{
                    "type": pf.MetaString(ref_type),
                    "number": doc.refcount[ref_type]
                })

            to_delete.update(attributes["to_delete"])

        subel = subel.next

    new_content = [
        pf.Span(el,
                classes=[
                    "labelled-{}".format(ref_type)] + to_wrap[el]["classes"],
                attributes=to_wrap[el]["attributes"],
                identifier=to_wrap[el]["label"]
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
