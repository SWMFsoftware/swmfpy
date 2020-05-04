"""A collection of tools to read, write, visualize with the
Space Weather Modeling Framework (SWMF).

### Modules

These are automatically imported.

- `swmfpy.io` Input/Output tools.
- `swmfpy.paramin` PARAM.in editing tools.
- `swmfpy.web` Internet data downloading/uploading tools.

### Extra Modules

These are not automatically imported. Might have extra dependancies.

*None yet.*
"""
__author__ = 'Qusai Al Shidi'
__license__ = 'MIT'
__version__ = '2020.1'
__maintainer__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'


import sys
assert sys.version_info >= (3, 6), "swmfpy requires Python >=3.6. Sorry :(."
from . import paramin
from . import io
from . import web

# This is straight from the format guide on spdf
OMNI_COLS = ('ID for IMF spacecraft',
             'ID for SW Plasma spacecraft',
             '# of points in IMF averages',
             '# of points in Plasma averages',
             'Percent interp',
             'Timeshift, sec',
             'RMS, Timeshift',
             'RMS, Phase front normal',
             'Time btwn observations, sec',
             'Field magnitude average, nT',
             'Bx, nT (GSE, GSM)',
             'By, nT (GSE)',
             'Bz, nT (GSE)',
             'By, nT (GSM)',
             'Bz, nT (GSM)',
             'RMS SD B scalar, nT',
             'RMS SD field vector, nT',
             'Flow speed, km/s',
             'Vx Velocity, km/s, GSE',
             'Vy Velocity, km/s, GSE',
             'Vz Velocity, km/s, GSE',
             'Proton Density, n/cc',
             'Temperature, K',
             'Flow pressure, nPa',
             'Electric field, mV/m',
             'Plasma beta',
             'Alfven mach number',
             'X(s/c), GSE, Re',
             'Y(s/c), GSE, Re',
             'Z(s/c), GSE, Re',
             'BSN location, Xgse, Re',
             'BSN location, Ygse, Re',
             'BSN location, Zgse, Re',
             'AE-index, nT',
             'AL-index, nT',
             'AU-index, nT',
             'SYM/D index, nT',
             'SYM/H index, nT',
             'ASY/D index, nT',
             'ASY/H index, nT',
             'PC(N) index',
             'Magnetosonic mach number')
