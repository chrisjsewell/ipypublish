import os
import json
import pytest
from jsonextended.utils import MockPath

from ipypublish.tests import TEST_FILES_DIR


@pytest.fixture
def ipynb1():
    ipynb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# a title\n", "\n", "some text\n"]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "source": [
                    "a=1\n",
                    "print(a)"
                ],
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": ["1\n"]
                    }
                ]
            }
        ],
        "metadata": {
            "test_name": "notebook1",
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.6.1"
            }},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    return MockPath('2test.ipynb', is_file=True,
                    content=json.dumps(ipynb))


@pytest.fixture
def ipynb2():
    ipynb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["hallo"]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "source": [
                    "a=1\n",
                    "print(a)"
                ],
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": ["1\n"]
                    }
                ]
            }
        ],
        "metadata": {
            "test_name": "notebook2",
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.6.1"
            }},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    return MockPath('1test.ipynb', is_file=True,
                    content=json.dumps(ipynb))


@pytest.fixture
def ipynb_with_bib():
    ipynb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["citation.\\cite{zelenyak_molecular_2016}"]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "source": [
                    "a=1\n",
                    "print(a)"
                ],
                "outputs": [
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": ["1\n"]
                    }
                ]
            }
        ],
        "metadata": {
            "test_name": "notebook2",
            "ipub": {"bibliography": "test.bib"},
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.6.1"
            }},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    return MockPath('test_with_bib.ipynb', is_file=True,
                    content=json.dumps(ipynb))


@pytest.fixture
def bibfile():
    return MockPath('test.bib', is_file=True,
                    content=r"""
@article{kirkeminde_thermodynamic_2012,
  title = {Thermodynamic Control of Iron Pyrite Nanocrystal Synthesis with High Photoactivity and Stability},
  volume = {1},
  issn = {2050-7496},
  doi = {10.1039/C2TA00498D},
  abstract = {Non-toxic, earth abundant nanostructured semiconductors have received extensive attention recently. One of the more highly studied materials has been iron pyrite (FeS2) due to its many different promising applications. Herein, we report the thermodynamically-controlled synthesis of FeS2 nanocrystals, dependent on the reaction temperature and chemical precursors, and a Lewis acid/base model to explain the shape-controlled synthesis. The surface facet-controlled photocatalytic activity and photostability were studied and explained. This work further advances the synthesis with pyrite structure control and surface facet-dictated applications, such as photovoltaics, photocatalysts and photoelectrochemical cells.},
  timestamp = {2017-07-06T00:26:10Z},
  langid = {english},
  number = {1},
  journaltitle = {Journal of Materials Chemistry A},
  shortjournal = {J. Mater. Chem. A},
  author = {Kirkeminde, Alec and Ren, Shenqiang},
  urldate = {2017-06-18},
  date = {2012-11-29},
  pages = {49--54}
}

@article{zelenyak_molecular_2016,
  title = {Molecular Dynamics Study of Perovskite Structures with Modified Interatomic Interaction Potentials},
  volume = {50},
  issn = {0018-1439, 1608-3148},
  doi = {10.1134/S0018143916050209},
  abstract = {The structure of compounds with the perovskite structure ABX3.},
  timestamp = {2017-07-06T00:19:33Z},
  langid = {english},
  number = {5},
  journaltitle = {High Energy Chemistry},
  shortjournal = {High Energy Chem},
  author = {Zelenyak, T. Yu and Kholmurodov, Kh T. and Tameev, A. R. and Vannikov, A. V. and Gladyshev, P. P.},
  urldate = {2017-07-06},
  date = {2016-09-01},
  pages = {400--405}
}
""")


@pytest.fixture
def directory(ipynb1, ipynb2):
    return MockPath('dir1', structure=[ipynb1, ipynb2])


# @pytest.fixture(scope="session")
# def hashkey_dict():
#     with open(os.path.join(TEST_FILES_DIR, "output_hashlibs.json")) as fobj:
#         data = json.load(fobj)
#     return data
