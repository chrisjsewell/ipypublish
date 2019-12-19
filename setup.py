#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup for ipypublish."""

import io
from importlib import import_module

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with io.open("README.md") as readme:
    readme_str = readme.read()

setup(
    name="ipypublish",
    version=import_module("ipypublish").__version__,
    description=(
        "A workflow for creating and editing publication ready "
        "scientific reports, from one or more Jupyter Notebooks"
    ),
    long_description=readme_str,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require={
        "sphinx": {"sphinx>=1.8", "sphinxcontrib-bibtex"},
        "tests": {
            "pytest>=3.6",
            "pytest-regressions",
            "pytest-cov",
            "coverage",
            "pillow",
            "nbsphinx>=0.5,<0.6",
            "ipykernel",
            "sphinx>=1.6",
            "sphinxcontrib-bibtex",
            "texsoup<=0.1.4",
        },
        "code_style": [
            "black==19.3b0",
            "pre-commit==1.17.0",
            "flake8<3.8.0,>=3.7.0",
            "doc8<0.9.0,>=0.8.0",
            "pygments",  # required by doc8
        ],
        "science": {"matplotlib", "numpy", "pandas", "sympy"},
        "rtd": {
            "recommonmark>=0.5",
            "pytest>=3.6",
            "pillow",
            "numpy",
            "matplotlib",
            "pandas",
            "sympy<1.3",
            "sphinx>=1.8",
            "sphinxcontrib-bibtex",
            "ipykernel",
            "ipywidgets>=7.5,<8",
        },
    },
    license="MIT",
    author="Chris Sewell",
    author_email="chrisj_sewell@hotmail.com",
    url="https://github.com/chrisjsewell/ipypublish",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Framework :: Sphinx :: Extension",
    ],
    keywords="python, jupyter-notebook, nbconvert, pandoc, latex, pdf",
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "nbpublish = ipypublish.frontend.nbpublish:run",
            "nbpresent = ipypublish.frontend.nbpresent:run",
            "ipubpandoc = ipypublish.filters_pandoc.main:pandoc_filters",
        ],
        "ipypublish.postprocessors": [
            "remove-blank-lines = ipypublish.postprocessors.stream_modify:RemoveBlankLines",
            "remove-trailing-space = ipypublish.postprocessors.stream_modify:RemoveTrailingSpace",
            "filter-output-files = ipypublish.postprocessors.stream_modify:FilterOutputFiles",
            "fix-slide-refs = ipypublish.postprocessors.stream_modify:FixSlideReferences",
            "pdf-export = ipypublish.postprocessors.pdfexport:PDFExport",
            "write-stream = ipypublish.postprocessors.to_stream:WriteStream",
            "write-text-file = ipypublish.postprocessors.file_actions:WriteTextFile",
            "remove-folder = ipypublish.postprocessors.file_actions:RemoveFolder",
            "write-resource-files = ipypublish.postprocessors.file_actions:WriteResourceFiles",
            "copy-resource-paths = ipypublish.postprocessors.file_actions:CopyResourcePaths",
            "reveal-server = ipypublish.postprocessors.reveal_serve:RevealServer",
            "run-sphinx = ipypublish.postprocessors.sphinx:RunSphinx [sphinx]",
            "convert-bibgloss = ipypublish.postprocessors.convert_bibgloss:ConvertBibGloss",
        ],
    },
)
