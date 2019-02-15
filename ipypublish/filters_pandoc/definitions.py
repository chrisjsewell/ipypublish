
IPUB_META_ROUTE = "ipub.pandoc"

ATTRIBUTE_CITE_CLASS = "attribute-Cite"
RAWSPAN_CLASS = "raw-content"
RAWDIV_CLASS = "raw-content"
CONVERTED_CITE_CLASS = "converted-Cite"
CONVERTED_OTHER_CLASS = "converted-Other"

# NB: it appears '-' is already used by sphinx, but '?' and '*' are also viable
PREFIX_MAP_LATEX = (('+', 'cref'), ('^', 'Cref'),
                    ('!', 'ref'), ('=', 'eqref'), ("", "cite"))
PREFIX_MAP_LATEX_R = (('cref', '+'), ('Cref', '^'),
                      ('ref', '!'), ('eqref', '='), ("cite", ""))
PREFIX_MAP_RST = (('+', 'numref'), ('^', 'numref'), ('!', 'ref'),
                  ('=', 'eq'), ("", "cite"))
PREFIX_MAP_RST_R = (('numref', '+'), ('ref', '!'), ('eq', '='), ("cite", ""))

CITE_HTML_NAMES = (
    ("Math", "eqn."),
    ("Image", "fig."),
    ("Table", "tbl.")
)

RST_KNOWN_ROLES = (
    "py:attr", "py:meth", "py:class", "py:func", "py:mod")
