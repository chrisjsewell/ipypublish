from ipypublish.filters_pandoc.main import jinja_filter
from ipypublish.filters_pandoc.utils import create_ipub_meta


def test_basic():

    out_str = jinja_filter("a", "rst", {}, {})
    assert out_str == "a"


def test_reference():

    out_str = jinja_filter("@label", "rst", {}, {})
    assert out_str == ":cite:`label`"


def test_reference_prefix():

    out_str = jinja_filter("+@label", "rst", {}, {})
    assert out_str == ":numref:`label`"


def test_option_in_nb_meta():

    out_str = jinja_filter(
        "+@label", "rst", create_ipub_meta({"use_numref": False}), {}
    )
    assert out_str == ":ref:`label`"


def test_option_in_cell_meta():

    out_str = jinja_filter(
        "+@label",
        "rst",
        create_ipub_meta({"use_numref": False}),
        create_ipub_meta({"use_numref": True}),
    )
    assert out_str == ":numref:`label`"


def test_option_in_top_matter():
    # TODO create ipub yaml from IPUB_META_ROUTE

    in_str = "\n".join(
        ["---", "ipub:", "  pandoc:", "    use_numref: true", "", "...", "", "+@label"]
    )

    out_str = jinja_filter(in_str, "rst", create_ipub_meta({"use_numref": False}), {})
    assert out_str == ":numref:`label`"


def test_at_notation_false():

    out_str = jinja_filter(
        "+@label", "rst", create_ipub_meta({"at_notation": False}), {}
    )
    assert out_str == "+ :cite:`label`"


def test_remove_filter():

    out_str = jinja_filter(
        "+@label", "rst", create_ipub_meta({"apply_filters": False}), {}
    )
    assert out_str == "+@label"


def test_complex_equation():

    in_source = [
        "$$\\begin{equation*}\n",
        "f(x) = \\left\\{\n",
        "\\begin{array}{ll}\n",
        "\\; x \\qquad x \\geq 0 \\\\\n",
        "\\; 0 \\qquad else\n",
        "\\end{array}\n",
        "\\right.\n",
        "\\end{equation*}$$",
    ]

    out_string = jinja_filter("".join(in_source), "rst", create_ipub_meta({}), {})
    expected = [
        ".. math::",
        "   :nowrap:",
        "",
        "   \\begin{equation*}",
        "   f(x) = \\left\\{",
        "   \\begin{array}{ll}",
        "   \\; x \\qquad x \\geq 0 \\\\",
        "   \\; 0 \\qquad else",
        "   \\end{array}",
        "   \\right.",
        "   \\end{equation*}",
    ]
    assert out_string.strip() == "\n".join(expected)
