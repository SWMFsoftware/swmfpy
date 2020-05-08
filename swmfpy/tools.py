#!/usr/bin/env python
"""Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import numpy as np


def get_v_gsm_from_omni(dict_omni):
    """Adds gsm values to the omni dictionary 

    This is helpful for the omni dict created with #swmfpy.web.get_omni_data()

    Args:
        dict_omni(dict): Dictionary with np.arrays in 'bz', 'by', 'bz_gse',
                         'by_gse', 'vx_gse', 'vy_gse'


    Returns:
        dict_omni with added 'vz' and 'vy' keys for gsm coordinates.

    Raises:
        KeyError: If above values don't exist.

    Examples:
        ```python
        import datetime as dt
        from swmfpy.web import get_omni_data
        from swmfpy.toos import get_v_gsm_from_omni

        time_period = (dt.datetime(2012, 2, 1), dt.datetime(2012, 4, 5))
        data = get_v_gsm_from_omni(get_omni_data(*time_period))

        # You should now have the omni dict with gsm values
        plot(data['times'], data['vz'])
        ```
    """
    # Author: Qusai Al Shidi
    # Email: qusai@umich.edu

    vy_gse, vz_gse = dict_omni['vy_gse'], dict_omni['vz_gse']
    by_gse, bz_gse = dict_omni['by_gse'], dict_omni['bz_gse']
    by_gsm, bz_gsm = dict_omni['by'], dict_omni['bz']
    velocity = np.sqrt(vx_gse**2 + vz_gse**2)
    theta = np.arctan(bz_gsm, by_gsm)
    dict_omni['vy'] = velocity*np.cos(theta)
    dict_omni['vz'] = velocity*np.sin(theta)
    return dict_omni


def _import_error_string(library):
    return (
        'Error importing drms. '
        f'Maybe try `pip install -U {library} --user ` .'
        )


def _make_line(value):
    """Makes the paramin line based on value type recursively
    """
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return '\t\t\t'.join([_make_line(v) for v in value])
    try:
        str(value)
    except Exception as error:
        raise TypeError(error,
                        '\nMust reduce to a str or a method that has',
                        '__str__ or __repr__')
    return str(value)


def _nearest(pivot, items):
    """Returns nearest point"""
    return min(items, key=lambda x: abs(x - pivot))
