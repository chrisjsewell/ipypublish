ETYPE_GLOSS = 'glsterm'
ETYPE_ACRONYM = 'glsacronym'
ETYPE_SYMBOL = 'glssymbol'

NEWGLOSS_FIELDS = (
    "name", "description", "plural", "symbol", "text", "sort"
)

NEWACRONYM_FIELDS = (
    "description", "plural", "longplural", "firstplural"
)


# TODO allow mapping
# DEFAULT_GLOSS_P2F = (("name", "name"),
#                      ("description", "description"),
#                      ("plural", "plural"),
#                      ("symbol", "symbol"),
#                      ("text", "text"),
#                      ("sort", "sort"))


# DEFAULT_ACRONYM_P2F = (("abbreviation", "abbreviation"),
#                        ("longname", "longname"),
#                        ("description", "description"),
#                        ("plural", "plural"),
#                        ("longplural", "longplural"),
#                        ("firstplural", "firstplural"))
