""" a panflute filter to override vs-code Markdown Preview Enhanced (MPE)
interpretation of RMarkdown python cells.

MPE expects cells to have braced attributes after code name;

::
    ```python {cmnd=true}
    print("hi")
    ```

whereas, in RMarkdown, the code name is included in the brace:

::

    ```{python ipub={'figure': {'caption': 'this is a caption'}}}
    print("hi")
    ```

See https://github.com/shd101wyy/vscode-markdown-preview-enhanced/issues/185

"""
# TODO remove when fixed?
import sys
import re
from panflute import Element, Doc, CodeBlock  # noqa: F401
import panflute as pf


def format_code_html(code, doc):
    # type: (CodeBlock, Doc) -> None
    if not (isinstance(code, CodeBlock)
            and doc.format in ("html", "html5")):
        return None

    if 'python' in code.attributes.get('data-info', ''):

        attr = code.attributes.get('data-info', '')

        parsed = "cmd='{}'".format(sys.executable)
        normed = '{{"cmd":"{}"'.format(sys.executable)

        if doc.last_id is None:
            this_id = 1
        else:
            this_id = doc.last_id + 1

        parsed = parsed + " id='{0}'".format(this_id)
        normed = normed + ',"id": "{0}"'.format(this_id)

        match = re.search("\\scontinue=([0-9]+)", attr)
        if match:
            parsed = parsed + " continue='{0}'".format(match.group(1))
            normed = normed + ',"continue":"{0}"'.format(match.group(1))

        if "matplotlib=true" in attr:
            parsed = parsed + " matplotlib=true"
            normed = normed + ',"matplotlib":"true"'

        normed = normed + "}"

        code.attributes['data-info'] = 'python {{{0}}}'.format(parsed)
        code.attributes['data-parsed-info'] = (
            '{{"language":"python","attributes":{0}}}'.format(normed))
        code.attributes['data-normalized-info'] = (
            '{{"language":"python","attributes":{0}}}'.format(normed))

        doc.last_id = this_id

        return [pf.Para(pf.Str("In [{}]:".format(this_id))), code]


def prepare(doc):
    # type: (Doc) -> None
    doc.last_id = None


def finalize(doc):
    # type: (Doc) -> None
    del doc.last_id


def main(doc=None):
    # type: (Doc) -> None
    return pf.run_filter(format_code_html,
                         prepare, finalize, doc=doc)


if __name__ == '__main__':
    main()
