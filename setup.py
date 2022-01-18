#!/usr/bin/env python
"""Setup script through setuptools. Simply run `python setup.py` to install
swmfpy.
"""
import setuptools


with open('README.md') as fh_readme:
    LONG_DESCRIPTION = fh_readme.read()

with open('requirements.txt') as fh_requirements:
    REQUIREMENTS = list(fh_requirements)

setuptools.setup(
    name='swmfpy',
    version='2022.1',
    author='Qusai Al Shidi',
    author_email='qusai@umich.edu',
    description='''A collection of tools for the Space Weather Modelling
 Framework''',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.umich.edu/swmf_software/swmfpy',
    packages=setuptools.find_packages(),
    license='LGPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
        ],
    install_requires=REQUIREMENTS,
    python_requires='>=3.6',
    extras_require={
        "tecplottools": "tecplot",
        "tecplottools": "h5py",
        "hmi": "drms",
        },
    package_data={
        'Documentation': ['DOCUMENTATION.markdown'],
        'TecplotDocumentation': ['TECPLOT.markdown'],
    },
    )
