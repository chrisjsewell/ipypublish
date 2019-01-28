import os
import pytest
from ipypublish.utils import pathlib   # noqa: F401
from ipypublish.frontend import nbpresent
from ipypublish.frontend import nbpublish


def test_nbpresent_dry_run(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    nbpresent.run([str(ipynb1), "--outpath", temp_folder,
                   "--dry-run", "--log-level", "debug"])


def test_nbpublish_dry_run(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    nbpublish.run([str(ipynb1), "--outpath", temp_folder,
                   "--dry-run", "--log-level", "debug"])


def test_nbpublish_write(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    nbpublish.run([str(ipynb1),
                   "--outformat", "latex_ipypublish_main",
                   "--outpath", temp_folder])
    assert os.path.exists(os.path.join(temp_folder,
                                       ipynb1.name.replace(".ipynb", ".tex")))


@pytest.mark.requires_latexmk
def test_nbpublish_to_pdf(temp_folder, ipynb1):
    # type: (str, pathlib.Path) -> None
    nbpublish.run([str(ipynb1),
                   "--outformat", "latex_ipypublish_main",
                   "--outpath", temp_folder,
                   "--create-pdf"])
    assert os.path.exists(os.path.join(temp_folder,
                                       ipynb1.name.replace(".ipynb", ".pdf")))

# TODO test plugins that are in user defined folders