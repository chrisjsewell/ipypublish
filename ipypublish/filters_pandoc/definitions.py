
IPUB_META_ROUTE = "ipub.pandoc"

ATTRIBUTE_CITE_CLASS = "attribute-Cite"
RAWSPAN_CLASS = "raw-span-content"
RAWDIV_CLASS = "raw-div-content"
CONVERTED_CITE_CLASS = "converted-Cite"
CONVERTED_DIRECTIVE_CLASS = "converted-rst-dir"
CONVERTED_OTHER_CLASS = "converted-Other"

# NB: it appears '-' and '^' are already used by sphinx
PREFIX_MAP = (
    ("", (
        ("classes", ()),
        ("attributes", (("latex", "cite"), ("rst", "cite")))
    )),
    ("+", (
        ("classes", ()),
        ("attributes", (("latex", "cref"), ("rst", "numref")))
    )),
    ("!", (
        ("classes", ()),
        ("attributes", (("latex", "ref"), ("rst", "ref")))
    )),
    ("=", (
        ("classes", ()),
        ("attributes", (("latex", "eqref"), ("rst", "eq")))
    )),
    ("?", (
        ("classes", ("capital",)),
        ("attributes", (("latex", "Cref"), ("rst", "numref")))
    )),
    ("&", (
        ("classes", ()),
        ("attributes", (("latex", "gls"), ("rst", "gls"))),
    )),
    ("%", (
        ("classes", ("capital",)),
        ("attributes", (("latex", "Gls"), ("rst", "glsc")))
    )),
)

PREFIX_MAP_LATEX_R = (
    ('cref', '+'),
    ('Cref', '?'),
    ('ref', '!'),
    ('eqref', '='),
    ("cite", ""),
    ("gls", "&"),
    ("Gls", "%")
    )
PREFIX_MAP_RST_R = (
    ('numref', '+'),
    ('ref', '!'),
    ('eq', '='),
    ("cite", ""),
    ("gls", "&"),
    ("glsc", "%")
    )

CITE_HTML_NAMES = (
    ("Math", "eqn."),
    ("Image", "fig."),
    ("Table", "tbl.")
)

RST_KNOWN_ROLES = (
    "py:attr", "py:meth", "py:class", "py:func", "py:mod")
