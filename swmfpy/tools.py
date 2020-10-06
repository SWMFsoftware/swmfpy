#!/usr/bin/env python
"""Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import datetime as dt
import numpy as np

def limit_growth(vector, factor=1.3, look_ahead=1, extensively=False):
    """This is a growth limiter for 1D vectors. It helps clean out spikes.

    Use this to clean out spikes in IMF data for example.

    Args:
        vector (numpy.array):
            A 1D array to clean.
        factor (float):
            The factor in which to limit growth. (default 1.3)
        look_ahead (int):
            How many frames to look ahead for growth.
        extensively (bool):
            Will keep refining until fully limited instead of one pass through.
            (default False)

    Returns:
        (numpy.array): Of limited vector.

    Raises:
        ValueError: If not given 1D array.

    Examples:
        ```python

        from datetime import datetime
        import matplotlib.pyplot as plt
        from swmfpy.web import get_omni_data
        from swmfpy.tools import limit_growth

        times = (datetime(2011, 8, 6), datetime(2011, 8, 7))
        data = get_omni_data(*times)
        plt.plot(data['times'], data['density'])
        plt.plot(data['times'], limit_growth(data['density'],
                                             extensively=True)
        ```
    """
    if sum(vector.shape) != vector.size:
        raise ValueError('limit_growth() only handles 1D arrays')

    limited = np.copy(vector)

    for i in range(look_ahead, len(limited)):
        if limited[i] > 0 and limited[i-look_ahead] > 0:
            limited[i] = min(limited[i-look_ahead]*factor,
                             max(limited[i], limited[i-look_ahead]/factor)
                            )
        if limited[i] < 0 and limited[i-look_ahead] < 0:
            limited[i] = min(limited[i-look_ahead]/factor,
                             max(limited[i], limited[i-look_ahead]*factor)
                            )

    return limited


def limit_changes(vector, change, constrictor=None, change2=None, look_ahead=1):
    """Limit the changes (jumps) of an array.

    This is different from #limit_growth() because growth works on a 
    multiplication factor but `limit_change()` works on absolute changes.

    Args:
        vector (numpy.array):
            Array in which to limit changes.
        change ((float, float)):
            Changes to limit `vector` by.
        constrictor (numpy.array):
            Array of same shape as `vector` in which if it is not growing
            then constrict further. This is useful for limiting compression
            behind shocks. If None, this won't apply (default None)
        change2 ((float, float)):
            Just like `change` but after constrictor has not grown. If None,
            this won't apply (default None)
        look_ahead (int):
            How many indeces ahead to check (default 1)

    Returns:
        (numpy.array): Of constricted `vector`.

    Raises:
        ValueError: If arrays are of different shapes or not 1D each.
        ValueError: If `change` tuple is not (negative, positive)

    Examples:
    """
    if sum(vector.shape) != vector.size:
        raise ValueError('vector must be 1D')
    if any(constrictor) and sum(constrictor.shape) != constrictor.size:
        raise ValueError('constrictor must be 1D')
    if change[0] > 0 or change[1] < 0:
        raise ValueError('change must be (negative, positive)')
    if change2[0] > 0 or change2[1] < 0:
        raise ValueError('change2 must be (negative, positive)')

    limited = np.copy(vector)
    for i in range(look_ahead, len(vector)):
        limited[i] = min(limited[i-1]+change[0],
                         max(limited[i-1]+change[1],
                             limited[i])
                        )

    if any(constrictor):
        for i in range(look_ahead, len(vector)):
            if constrictor[i] <= constrictor[i-1]:
                limited[i] = min(limited[i-1]+change2[0],
                                 max(limited[i-1]+change2[1],
                                     limited[i])
                                )

    return limited



def interp_nans(x_vals, y_vals):
    """Returns a numpy array with NaNs interpolated.

    Args:
        x_vals (np.array):
            x values to interpolate.
        y_vals (np.array):
            y values including NaNs.

    Returns:
        (np.array): numpy array with NaNs interpolated.
    """

    nonans = np.nonzero(np.isnan(y_vals) == 0)
    return np.interp(x_vals, x_vals[nonans], y_vals[nonans])


def carrington_rotation_number(the_time='now'):
    """Returns the carrington rotation

    Args:
        the_time (datetime.datetime/str): The time to convert to carrington
                                          rotation.

    Returns:
        (int): Carrington Rotation
    """
    if the_time == 'now':
        return carrington_rotation_number(dt.datetime.now())
    if isinstance(the_time, str):
        return carrington_rotation_number(dt.datetime.fromisoformat(the_time))
    return int((the_time.toordinal() - 676715.2247)/27.2753)


def _import_error_string(library):
    return (
        f'Error importing {library}. '
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
