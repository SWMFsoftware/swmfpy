"""A collection of tools to read, write, visualize with the
Space Weather Modeling Framework (SWMF).

Modules
-------

These are automatically imported.

- `swmfpy.io` Input/Output tools.
- `swmfpy.paramin` PARAM.in editing tools.
- `swmfpy.web` Internet data downloading/uploading tools.

Extra Modules
-------------

These are not automatically imported. Might have extra dependancies.

*None yet.*
"""
__author__ = 'Qusai Al Shidi'
__license__ = 'MIT'
__version__ = '2020.0'
__maintainer__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'


from . import paramin
from . import io
from . import web
