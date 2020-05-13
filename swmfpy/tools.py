#!/usr/bin/env python
"""Tools to be used in swmfpy functions and classes. Some of the functions are
*hidden functions*.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import numpy as np
from scipy.optimize import newton, check_grad


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

    b_gsm = [dict_omni['bx'], dict_omni['by'], dict_omni['bz']]
    b_gse = [dict_omni['bx'], dict_omni['by_gse'], dict_omni['bz_gse']]
    v_gse = [dict_omni['vx_gse'], dict_omni['vy_gse'], dict_omni['vz_gse']]

    def check_prime(func, fprime, *args):
        'Make sure my derivatives are correct'
        assert check_grad(func, fprime, [0.1], *args) < 1.e-3, 'bad grad'

    def rot_y(theta, vec):
        'rotate y in yz plane'
        return vec[1]*np.cos(theta)-vec[2]*np.sin(theta)

    def rot_y_prime(theta, vec):
        'rotate y in yz plane'
        return -vec[1]*np.sin(theta)-vec[2]*np.cos(theta)

    check_prime(rot_y, rot_y_prime, (1, 1, 1))

    def rot_y_prime2(theta, vec):
        'rotate y in yz plane'
        return -vec[1]*np.cos(theta)+vec[2]*np.sin(theta)

    check_prime(rot_y_prime, rot_y_prime2, (1, 1, 1))

    def rot_z(theta, vec):
        'rotate z in yz plane'
        return vec[1]*np.sin(theta)+vec[2]*np.cos(theta)

    def rot_z_prime(theta, vec):
        'rotate z in yz plane'
        return vec[1]*np.cos(theta)-vec[2]*np.sin(theta)

    check_prime(rot_z, rot_z_prime, (1, 1, 1))

    def rot_z_prime2(theta, vec):
        'rotate z in yz plane'
        return -vec[1]*np.sin(theta)-vec[2]*np.cos(theta)

    check_prime(rot_z_prime, rot_z_prime2, (1, 1, 1))

    def opt_func(theta, vec_p, vec):
        'The two functions to optimize'
        opt_y = vec_p[1] - rot_y(theta, vec)
        opt_z = vec_p[2] - rot_z(theta, vec)
        return opt_y + opt_z

    def opt_func_prime(theta, _, vec):
        'The two functions to optimize'
        opt_y = -rot_y_prime(theta, vec)
        opt_z = -rot_z_prime(theta, vec)
        return opt_y + opt_z

    check_prime(opt_func, opt_func_prime, (1, 1, 1), (1, 1, 1))

    def opt_func_prime2(theta, _, vec):
        'The two functions to optimize'
        opt_y = -rot_y_prime2(theta, vec)
        opt_z = -rot_z_prime2(theta, vec)
        return opt_y + opt_z

    check_prime(opt_func_prime, opt_func_prime2, (1, 1, 1), (1, 1, 1))

    angle = newton(opt_func, np.zeros_like(b_gsm[0]), args=(b_gsm, b_gse),
                   fprime=opt_func_prime, fprime2=opt_func_prime2, tol=1.e-2)

    dict_omni.update({
        'vx': dict_omni['vx_gse'],
        'vy': rot_y(angle, v_gse),
        'vz': rot_z(angle, v_gse),
        })
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
