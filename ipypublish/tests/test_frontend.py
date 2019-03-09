import os
import pytest
from ipypublish.utils import pathlib   # noqa: F401
from ipypublish.frontend import nbpresent
from ipypublish.frontend import nbpublish


@pytest.mark.ipynb('basic_nb')
def test_nbpresent_bad_exporter(ipynb_app):
    # type: (str, pathlib.Path) -> None
    assert 1 == nbpresent.run([str(ipynb_app.input_file),
                               "-f", "non-existent",
                               "--outpath", str(ipynb_app.converted_path),
                               "--dry-run", "--log-level", "debug"])


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_bad_exporter(ipynb_app):
    # type: (str, pathlib.Path) -> None
    assert 1 == nbpublish.run([str(ipynb_app.input_file),
                               "-f", "non-existent",
                               "--outpath", str(ipynb_app.converted_path),
                               "--dry-run", "--log-level", "debug"])


@pytest.mark.ipynb('basic_nb')
def test_nbpresent_dry_run(ipynb_app):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpresent.run([str(ipynb_app.input_file),
                               "--outpath", str(ipynb_app.converted_path),
                               "--dry-run", "--log-level", "debug", "-pt"])


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_dry_run(ipynb_app):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb_app.input_file),
                               "--outpath", str(ipynb_app.converted_path),
                               "--dry-run", "--log-level", "debug", "-pt"])


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_dry_run_with_external_plugin(
        ipynb_app, external_export_plugin):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb_app.input_file),
                               "--outformat", str(external_export_plugin),
                               "--outpath", str(ipynb_app.converted_path),
                               "--dry-run", "--log-level", "debug", "-pt"])


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_dry_run_with_external_plugin_key(
        ipynb_app, external_export_plugin):
    # type: (str, pathlib.Path, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb_app.input_file),
                               "--export-paths",
                               str(external_export_plugin.parent),
                               "--outformat",
                               os.path.splitext(
                                   str(external_export_plugin.name))[0],
                               "--outpath", str(ipynb_app.converted_path),
                               "--dry-run", "--log-level", "debug", "-pt"])


def test_nbpresent_list_exports():
    with pytest.raises(SystemExit) as out:
        nbpresent.run(["--list-exporters"])
        assert out.type == SystemExit
        assert out.value.code == 0


def test_nbpublish_list_exports():
    with pytest.raises(SystemExit) as out:
        nbpublish.run(["--list-exporters"])
        assert out.type == SystemExit
        assert out.value.code == 0


@pytest.mark.ipynb('basic_nb')
def test_nbpublish_write(ipynb_app):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb_app.input_file),
                               "--outformat", "latex_ipypublish_main",
                               "--outpath", str(ipynb_app.converted_path),
                               "-pt"])
    assert ipynb_app.converted_path.joinpath(
        ipynb_app.input_file.name.replace(".ipynb", ".tex")).exists()


@pytest.mark.requires_latexmk
@pytest.mark.ipynb('basic_nb')
def test_nbpublish_to_pdf(ipynb_app):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb_app.input_file),
                               "--outformat", "latex_ipypublish_main",
                               "--outpath", str(ipynb_app.converted_path),
                               "--create-pdf", "-pt"])
    assert ipynb_app.converted_path.joinpath(
        ipynb_app.input_file.name.replace(".ipynb", ".pdf")).exists()
