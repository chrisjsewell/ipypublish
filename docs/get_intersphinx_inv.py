#!/usr/bin/env python


def fetch_inventory(uri):
    """Read a Sphinx inventory file into a dictionary."""

    class MockConfig(object):
        intersphinx_timeout = None  # type: int
        tls_verify = False

    class MockApp(object):
        srcdir = ""
        config = MockConfig()

        def warn(self, msg):
            warnings.warn(msg)

    return intersphinx.fetch_inventory(MockApp(), "", uri)


if __name__ == "__main__":
    from sphinx.ext import intersphinx
    import warnings

    # uri = 'http://jinja.pocoo.org/docs/dev/objects.inv'
    # uri = "http://nbconvert.readthedocs.io/en/latest/objects.inv"
    # uri = "http://nbformat.readthedocs.io/en/latest/objects.inv"
    # uri = "https://docutils.readthedocs.io/en/sphinx-docs/objects.inv"
    # uri = "https://traitlets.readthedocs.io/en/latest/objects.inv"
    # uri = "https://networkx.github.io/documentation/stable/objects.inv"
    # uri = "http://docs.scipy.org/doc/scipy/reference/objects.inv"
    # uri = "http://pillow.readthedocs.org/en/latest/objects.inv"
    uri = "http://www.sphinx-doc.org/en/latest/objects.inv"

    # Read inventory into a dictionary
    inv = fetch_inventory(uri)
    # Or just print it
    intersphinx.debug(["", uri])
