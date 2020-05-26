#!/usr/bin/env python
"""Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'


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
