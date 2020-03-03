"""Tools for SWMF

swmfpy
======

A collection of tools to read, write, visualize with the
Space Weather Modeling Framework (SWMF).

Modules
-------

These are automatically imported.

- swmfpy.io: Input/Output tools.
- paramin.io: PARAM.in editing tools.
- web.io: Internet tools.

Extra Modules
-------------

These are not automatically imported. Might have extra dependancies.

*Non yet.*
"""
__author__ = "Qusai Al Shidi"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Qusai Al Shidi"
__email__ = "qusai@umich.edu"


from . import paramin
from . import io
from . import web
