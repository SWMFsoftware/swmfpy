#!/usr/bin/env python
"""Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'


def _import_error_string(library):
        return f'Error importing drms. Maybe try `pip install -U {library} --user ` .'


def _nearest(pivot, items):
    """Returns nearest point"""
    return min(items, key=lambda x: abs(x - pivot))
