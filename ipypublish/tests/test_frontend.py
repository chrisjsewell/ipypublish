import os
import pytest
from ipypublish.utils import pathlib   # noqa: F401
from ipypublish.frontend import nbpresent
from ipypublish.frontend import nbpublish


def test_nbpresent_bad_exporter(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    assert 1 == nbpresent.run([str(ipynb1), "-f", "non-existent",
                               "--outpath", temp_folder,
                               "--dry-run", "--log-level", "debug"])


def test_nbpublish_bad_exporter(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    assert 1 == nbpublish.run([str(ipynb1),  "-f", "non-existent",
                               "--outpath", temp_folder,
                               "--dry-run", "--log-level", "debug"])


def test_nbpresent_dry_run(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpresent.run([str(ipynb1), "--outpath", temp_folder,
                               "--dry-run", "--log-level", "debug", "-pt"])


def test_nbpublish_dry_run(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb1), "--outpath", temp_folder,
                               "--dry-run", "--log-level", "debug", "-pt"])


def test_nbpublish_dry_run_with_external_plugin(
        temp_folder, ipynb1, external_export_plugin):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb1),
                               "--outformat", str(external_export_plugin),
                               "--outpath", temp_folder,
                               "--dry-run", "--log-level", "debug", "-pt"])


def test_nbpublish_dry_run_with_external_plugin_key(
        temp_folder, ipynb1, external_export_plugin):
    # type: (str, pathlib.Path, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb1),
                               "--export-paths",
                               str(external_export_plugin.parent),
                               "--outformat",
                               os.path.splitext(
                                   str(external_export_plugin.name))[0],
                               "--outpath", temp_folder,
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


def test_nbpublish_write(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb1),
                               "--outformat", "latex_ipypublish_main",
                               "--outpath", temp_folder, "-pt"])
    assert os.path.exists(os.path.join(temp_folder,
                                       ipynb1.name.replace(".ipynb", ".tex")))


@pytest.mark.requires_latexmk
def test_nbpublish_to_pdf(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    assert 0 == nbpublish.run([str(ipynb1),
                               "--outformat", "latex_ipypublish_main",
                               "--outpath", temp_folder,
                               "--create-pdf", "-pt"])
    assert os.path.exists(os.path.join(temp_folder,
                                       ipynb1.name.replace(".ipynb", ".pdf")))
