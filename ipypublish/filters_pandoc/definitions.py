
IPUB_META_ROUTE = "ipub.pandoc"

ATTRIBUTE_CITE_CLASS = "attribute-Cite"


# NB: it appears '-' is already used by sphinx, but '?' and '*' are viable
PREFIX_MAP_LATEX = (('+', 'cref'), ('^', 'Cref'),
                    ('!', 'ref'), ('=', 'eqref'), ("", "cite"))
PREFIX_MAP_LATEX_R = (('cref', '+'), ('Cref', '^'),
                      ('ref', '!'), ('eqref', '='), ("cite", ""))
PREFIX_MAP_RST = (('+', 'numref'), ('^', 'numref'), ('!', 'ref'),
                  ('=', 'eq'), ("", "cite"))
PREFIX_MAP_RST_R = (('numref', '+'), ('ref', '!'), ('eq', '='), ("cite", ""))