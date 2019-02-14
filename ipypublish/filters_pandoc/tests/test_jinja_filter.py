from ipypublish.filters_pandoc.main import jinja_filter


def test_basic():

    out_str = jinja_filter(
        "a", "rst", {}, {}
    )
    assert out_str == "a"


def test_reference():

    out_str = jinja_filter(
        "@label", "rst", {}, {}
    )
    assert out_str == ":cite:`label`"


def test_reference_prefix():

    out_str = jinja_filter(
        "+@label", "rst", {}, {}
    )
    assert out_str == ":numref:`label`"


def test_option_in_nb_meta():

    out_str = jinja_filter(
        "+@label", "rst", {"ipub": {"use_numref": False}}, {}
    )
    assert out_str == ":ref:`label`"


def test_option_in_cell_meta():

    out_str = jinja_filter(
        "+@label", "rst", {"ipub": {"use_numref": False}},
        {"ipub": {"use_numref": True}}
    )
    assert out_str == ":numref:`label`"


def test_option_in_top_matter():

    out_str = jinja_filter(
        "\n".join([
            "---",
            "ipub:",
            "    use_numref: True",
            "---",
            "+@label"
        ]),
        "rst", {"ipub": {"use_numref": False}}, {}
    )
    assert out_str == ":numref:`label`"


def test_at_notation_false():

    out_str = jinja_filter(
        "+@label", "rst", {"ipub": {"at_notation": False}}, {}
    )
    assert out_str == "+ :cite:`label`"


def test_remove_filter():

    out_str = jinja_filter(
        "+@label", "rst", {"ipub": {"filter_mkdown": False}}, {}
    )
    assert out_str == "+@label"