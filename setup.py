#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup for ipypublish."""

import io
from importlib import import_module

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
with open('test_requirements.txt') as f:
    test_requirements = f.read().splitlines()

with io.open('README.md') as readme:
    readme_str = readme.read()

setup(
    name='ipypublish',
    version=import_module('ipypublish').__version__,
    description=(
        'A workflow for creating and editing publication ready '
        'scientific reports, from one or more Jupyter Notebooks'),
    long_description=readme_str,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={
        "docs": {
            "sphinx"
        },
        "sphinx": {
            "sphinx>=1.6",
            "docutils",
            "sphinxcontrib-bibtex"
        }
    },
    license='MIT',
    author='Chris Sewell',
    author_email='chrisj_sewell@hotmail.com',
    url='https://github.com/chrisjsewell/ipypublish',
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Financial and Insurance Industry',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
    ],
    keywords='python, jupyter-notebook, nbconvert, pandoc, latex, pdf',
    zip_safe=True,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nbpublish = ipypublish.frontend.nbpublish:run',
            'nbpresent = ipypublish.frontend.nbpresent:run'
        ],
        'ipypublish.postprocessors': [
            'remove-blank-lines = ipypublish.postprocessors.stream_modify:RemoveBlankLines',
            'remove-trailing-space = ipypublish.postprocessors.stream_modify:RemoveTrailingSpace',
            'filter-output-files = ipypublish.postprocessors.stream_modify:FilterOutputFiles',
            'fix-slide-refs = ipypublish.postprocessors.stream_modify:FixSlideReferences',
            'pdf-export = ipypublish.postprocessors.pdfexport:PDFExport',
            'write-stream = ipypublish.postprocessors.to_stream:WriteStream',
            'write-text-file = ipypublish.postprocessors.file_actions:WriteTextFile',
            'remove-folder = ipypublish.postprocessors.file_actions:RemoveFolder',
            'write-resource-files = ipypublish.postprocessors.file_actions:WriteResourceFiles',
            'copy-resource-paths = ipypublish.postprocessors.file_actions:CopyResourcePaths',
            'reveal-server = ipypublish.postprocessors.reveal_serve:RevealServer',
            'run-sphinx = ipypublish.postprocessors.sphinx:RunSphinx [sphinx]'
        ]
    }
)
