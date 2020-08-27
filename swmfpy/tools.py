#!/usr/bin/env python
"""Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import datetime as dt
import numpy as np


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
