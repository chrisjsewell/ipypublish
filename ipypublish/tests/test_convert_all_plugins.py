import os
import sys
import pytest

from ipypublish.convert.config_manager import iter_all_export_paths


@pytest.mark.parametrize(
    "plugin_name,plugin_path",
    list(iter_all_export_paths())
)
@pytest.mark.ipynb('basic_nb')
def test_basic_all_plugins(ipynb_app, plugin_name, plugin_path):

    if ((plugin_name in ["sphinx_ipypublish_all.ext"]
         or "exec" in plugin_name) and sys.version_info[0] < 3):
        # TODO this fails because the kernel is set as python3 in the notebook
        # could add a replacement variable e.g. ${pykernel}
        # and allow parsing of it to main.publish (default = "")
        return

    ipynb_app.run({"conversion": plugin_name})

    # no output file to compare
    if plugin_name in [
            "python_with_meta_stream",
            "sphinx_ipypublish_all.ext", "sphinx_ipypublish_all.ext.noexec"]:
        return

    # test build exists only
    if plugin_name in [
            "sphinx_ipypublish_all.run", "sphinx_ipypublish_main.run"]:
        outpath = ipynb_app.converted_path.joinpath(
            "build", "html",
            os.path.splitext(ipynb_app.input_file.name)[0] + ".html")
        assert outpath.exists()
        return

    ipynb_app.assert_converted_exists()
    ipynb_app.assert_converted_equals_expected(plugin_name)
