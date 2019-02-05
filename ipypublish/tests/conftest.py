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
def ipynb_with_attach():
    return {
        "input_file": pathlib.Path(os.path.join(
            TEST_FILES_DIR, 'nb_with_attachment',
            'nb_with_attachment.ipynb')),
        "latex_ipypublish_main": pathlib.Path(os.path.join(
            TEST_FILES_DIR, 'nb_with_attachment',
            'latex_ipypublish_main.tex'))
    }


@pytest.fixture
def ipynb_with_bib():
    return pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb_with_bib.ipynb'))


@pytest.fixture
def bibfile():
    return pathlib.Path(os.path.join(TEST_FILES_DIR, 'test.bib'))


@pytest.fixture
def external_export_plugin():
    return pathlib.Path(os.path.join(TEST_FILES_DIR,
                                     'example_new_plugin.json'))


@pytest.fixture
def temp_folder():
    out_folder = tempfile.mkdtemp()
    yield out_folder
    shutil.rmtree(out_folder)


@pytest.fixture
def ipynb_folder(temp_folder, ipynb1, ipynb2):

    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb1.ipynb'),
                    os.path.join(temp_folder, 'ipynb1.ipynb'))
    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb2.ipynb'),
                    os.path.join(temp_folder, 'ipynb2.ipynb'))
    yield temp_folder


@pytest.fixture
def ipynb_folder_with_external(temp_folder):

    folder = os.path.join(temp_folder, "ipynb_with_external")
    os.makedirs(folder)

    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb_with_external',
                                 'ipynb_with_external.ipynb'),
                    os.path.join(folder, 'ipynb_with_external.ipynb'))
    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb_with_external',
                                 'example.bib'),
                    os.path.join(folder, 'example.bib'))
    shutil.copyfile(os.path.join(TEST_FILES_DIR, 'ipynb_with_external',
                                 'logo_example.png'),
                    os.path.join(folder, 'logo_example.png'))

    tex = pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb_with_external',
                                    'ipynb_with_external.tex'))
    html = pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb_with_external',
                                     'ipynb_with_external.html'))
    slides = pathlib.Path(os.path.join(TEST_FILES_DIR, 'ipynb_with_external',
                                       'ipynb_with_external.slides.html'))

    yield {
        "input_folder": folder,
        "latex_ipypublish_main": tex,
        "html_ipypublish_main": html,
        "slides_ipypublish_main": slides
    }
