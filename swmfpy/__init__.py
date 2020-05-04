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

# This is straight from the format guide on spdf with nicer names as second col
OMNI_COLS = (('ID for IMF spacecraft', 'id_imf'),
             ('ID for SW Plasma spacecraft', 'id_sw'),
             ('# of points in IMF averages', 'num_avg_imf'),
             ('# of points in Plasma averages', 'num_avg_sw'),
             ('Percent interp', 'interp'),
             ('Timeshift, sec', 'timeshift'),
             ('RMS, Timeshift', 'rms_timeshift'),
             ('RMS, Phase front normal', 'rms_phase'),
             ('Time btwn observations, sec', 'dt'),
             ('Field magnitude average, nT', 'b'),
             ('Bx, nT (GSE, GSM)', 'bx'),
             ('By, nT (GSE)', 'by_gse'),
             ('Bz, nT (GSE)', 'bz_gse'),
             ('By, nT (GSM)', 'by'),
             ('Bz, nT (GSM)', 'bz'),
             ('RMS SD B scalar, nT', 'rms_sd_b'),
             ('RMS SD field vector, nT', 'rms_sd_field'),
             ('Flow speed, km/s', 'v'),
             ('Vx Velocity, km/s, GSE', 'vx_gse'),
             ('Vy Velocity, km/s, GSE', 'vy_gse'),
             ('Vz Velocity, km/s, GSE', 'vz_gse'),
             ('Proton Density, n/cc', 'density'),
             ('Temperature, K', 'temperature'),
             ('Flow pressure, nPa', 'pressure'),
             ('Electric field, mV/m', 'e'),
             ('Plasma beta', 'beta'),
             ('Alfven mach number', 'alfven_mach'),
             ('X(s/c), GSE, Re', 'x_gse'),
             ('Y(s/c), GSE, Re', 'y_gse'),
             ('Z(s/c), GSE, Re', 'z_gse'),
             ('BSN location, Xgse, Re', 'bsn_x_gse'),
             ('BSN location, Ygse, Re', 'bsn_y_gse'),
             ('BSN location, Zgse, Re', 'bsn_z_gse'),
             ('AE-index, nT', 'ae'),
             ('AL-index, nT', 'al'),
             ('AU-index, nT', 'au'),
             ('SYM/D index, nT', 'sym_d'),
             ('SYM/H index, nT', 'sym_h'),
             ('ASY/D index, nT', 'asy_d'),
             ('ASY/H index, nT', 'asy_h'),
             ('PC(N) index', 'pc_n'),
             ('Magnetosonic mach number', 'mach'),
             )
