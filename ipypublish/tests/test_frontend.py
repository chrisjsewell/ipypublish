import pytest
from jsonextended.utils import MockPath   # noqa: F401
from ipypublish.frontend import nbpresent
from ipypublish.frontend import nbpublish


def test_nbpresent_dry_run(ipynb1):
    # type: (MockPath) -> None
    with ipynb1.maketemp() as fpath:
        nbpresent.run([str(fpath), "--dry-run", "--log-level", "debug"])


def test_nbpublish_dry_run(ipynb1):
    # type: (MockPath) -> None
    with ipynb1.maketemp() as fpath:
        nbpublish.run([str(fpath), "--dry-run", "--log-level", "debug"])


def test_nbpublish_write(ipynb1):
    # type: (MockPath) -> None
    with ipynb1.maketemp() as fpath:
        nbpublish.run([str(fpath),
                       "--outformat", "latex_ipypublish_main",
                       "--outpath", str(fpath.parent)])
        assert fpath.parent.joinpath(
            fpath.name.replace(".ipynb", ".tex")).exists()


@pytest.mark.requires_latexmk
def test_nbpublish_to_pdf(ipynb1):
    # type: (MockPath) -> None
    with ipynb1.maketemp() as fpath:
        nbpublish.run([str(fpath),
                       "--outformat", "latex_ipypublish_main",
                       "--outpath", str(fpath.parent),
                       "--create-pdf"])
        assert fpath.parent.joinpath(
            fpath.name.replace(".ipynb", ".pdf")).exists()
