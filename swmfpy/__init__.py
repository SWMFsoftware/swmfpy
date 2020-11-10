"""A collection of tools to read, write, visualize with the
Space Weather Modeling Framework (SWMF).

### Modules

These are automatically imported.

- `swmfpy.io` Input/Output tools.
- `swmfpy.paramin` PARAM.in editing tools.
- `swmfpy.web` Internet data downloading/uploading tools.

### Extra Modules

These must be imported manually.

- `swmfpy.tools` Tools used in swmfpy. You might find these useful but it is
  unecessary.
- `swmfpy.tecplottools` Tools for working with the Tecplot visualization
  software. Requires a Tecplot license and the pytecplot python package.
"""
__author__ = 'Qusai Al Shidi'
__license__ = 'LGPLv3'
__version__ = '2020.10'
__maintainer__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'
__credits__ = 'University of Michigan, Climate and Space Sciences & Engineering'


import sys
from . import paramin
from . import io
from . import web
assert sys.version_info >= (3, 6), "swmfpy requires Python >=3.6. Sorry :(."


def write_imf_from_omni(time_from, time_to, filename='IMF.dat', **kwargs):
    """Writes an IMF.dat file for the geospace model runs for a specific time
    period.

    Args:
        time_from (datetime.datetime): Time to begin omni data retrieval
        time_to (datetime.datetime): Time to end omni data retrieval
        filename (str): The filename for the dat file, defaults to 'IMF.dat'.

    **kwargs:
        see #swmfpy.io.write_imf_input() and #swmfpy.web.get_omni_data()

    Returns:
        (dict): Dictionary of omni data.

    Examples:
        Using this function is simple:
        ```python
        import swmfpy
        import datetime as dt
        times = (dt.datetime(2014, 2, 2), dt.datetime(2014, 2, 4))
        # Usually the kwargs are unecessary
        swmfpy.write_imf_input(*times)
        # Sometimes this
        swmfpy.write_imf_input(*times, filename='run/IMF.dat')
        ```
    """
    omni_data = web.get_omni_data(time_from, time_to, **kwargs)
    commands = ['#COOR', 'GSE']
    if kwargs.get('commands', None):
        kwargs['commands'] += commands
    else:
        kwargs['commands'] = commands
    column_keys = ['times',
                   'bx', 'by_gse', 'bz_gse', 'vx_gse', 'vy_gse', 'vz_gse',
                   'density', 'temperature']
    io.write_imf_input(omni_data, filename, column_keys=column_keys, **kwargs)
    return omni_data
