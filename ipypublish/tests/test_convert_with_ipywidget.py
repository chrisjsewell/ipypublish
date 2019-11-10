import sys

import pytest


@pytest.mark.skipif(
    sys.version_info[:2] == (3, 5), reason="json_dumps puts keys in different order"
)
@pytest.mark.ipynb("nb_with_ipywidget")  # , out_to_temp=False)
def test_ipywidget_sphinx_rst(ipynb_app):
    """The notebook contains an ipywidgets and the widget state has been saved."""

    ipynb_app.run({"conversion": "sphinx_ipypublish_all"})

    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_equals_expected("main")
