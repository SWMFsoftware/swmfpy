#!/usr/bin/env python
"""Setup script through setuptools. Simply run `python setup.py` to install
swmfpy.
"""
import setuptools


with open('README.markdown') as readme_fh:
    LONG_DESCRIPTION = readme_fh.read()

setuptools.setup(
    name='swmfpy',
    version='2020.1',
    author='Qusai Al Shidi',
    author_email='qusai@umich.edu',
    description='''A collection of tools for the Space Weather Modelling
 Framework''',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.umich.edu/swmf_software/swmfpy',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires='>=3.6'
    )
