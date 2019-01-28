import os
import shutil
import tempfile
import pytest

from ipypublish.utils import pathlib
from ipypublish.tests import TEST_FILES_DIR


@pytest.fixture
def ipynb1():
    return pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb1.ipynb'))


@pytest.fixture
def ipynb2():
    return pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb2.ipynb'))


@pytest.fixture
def ipynb_with_bib():
    return pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb_with_bib.ipynb'))


@pytest.fixture
def bibfile():
    return pathlib.Path(os.path.join(TEST_FILES_DIR, 'test.bib'))


@pytest.fixture
def ipynb_folder(temp_folder, ipynb1, ipynb2):

    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb1.ipynb'),
                    os.path.join(temp_folder, 'ipynb1.ipynb'))
    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb2.ipynb'),
                    os.path.join(temp_folder, 'ipynb2.ipynb'))
    yield temp_folder


@pytest.fixture
def temp_folder():
    out_folder = tempfile.mkdtemp()
    yield out_folder
    shutil.rmtree(out_folder)
