#!/usr/bin/env python3
"""swmfpy is a tool to read and visualize SWMF data
"""
__author__ = "Qusai Al Shidi"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Qusai Al Shidi"
__email__ = "qusai@umich.edu"

import numpy as np
import pandas as pd


def omni_to_df(filename, filtering=False, **kwargs):
    """Take an OMNI csv file from cdaweb.sci.gsfc.nasa.gov
    and turn it into a pandas.DataFrame.

    Parameters:
        fnames: dict with filenames from omni .lst files. The keys must be:
            density, temperature, magnetic_field, velocity
        filtering: default=False Remove points where the value
                          is >sigma (default: sigma=3) from mean.

    Returns: pandas.DataFrame object with solar wind data

    Make sure to download the csv files with cdaweb.sci.gsfc.nasa.gov
    the header seperated into a json file for safety.

    This only tested with OMNI data specifically.

    Other Parameters:
        coarseness: default=3, Number of standard deviations above which to remove
                    if filtering=True.
        clean: default=True, Clean the omni data of bad data points (recommended to keep this True)

    """
    # Read the csv files and set the index to dates
    with open(filename, 'r') as datafile:
        data = pd.read_csv(datafile)
    data.set_index(pd.to_datetime(data[data.columns[0]]), inplace=True)
    data.drop(columns=data.columns[0], inplace=True)
    data.index.name = "Time [UT]"
    data.rename(inplace = True, 
                columns={'BX__GSE_nT': 'Bx [nT]',
                         'BY__GSE_nT': 'By [nT]',
                         'BZ__GSE_nT': 'Bz [nT]',
                         'VX_VELOCITY__GSE_km/s': 'Vx [km/s]',
                         'VY_VELOCITY__GSE_km/s': 'Vy [km/s]',
                         'VZ_VELOCITY__GSE_km/s': 'Vz [km/s]',
                         'PROTON_DENSITY_n/cc': 'Rho [n/cc]',
                         'TEMPERATURE_K': 'T [K]'})

    # clean bad data
    if kwargs.get('clean', True):
        data["By [nT]"] = data["By [nT]"][data["By [nT]"].abs() < 80.]
        data["Bx [nT]"] = data["Bx [nT]"][data["Bx [nT]"].abs() < 80.]
        data["Bz [nT]"] = data["Bz [nT]"][data["Bz [nT]"].abs() < 80.]
        data["Rho [n/cc]"] = data["Rho [n/cc]"][data["Rho [n/cc]"] < 500.]
        data["Vx [km/s]"] = data["Vx [km/s]"][data["Vx [km/s]"].abs() < 2000.]
        data["Vz [km/s]"] = data["Vz [km/s]"][data["Vz [km/s]"].abs() < 1000.]
        data["Vy [km/s]"] = data["Vy [km/s]"][data["Vy [km/s]"].abs() < 1000.]
        data["T [K]"] = data["T [K]"][data["T [K]"] < 1.e7]

    if filtering:
        coarse_filtering(data, kwargs.get('coarseness', 3))
    return data.interpolate().bfill().ffill()

def coarse_filtering(data, coarseness=3):
    """Applies coarse filtering to a pandas.DataFrame"""
    for column in data.columns:
        mean = data[column].abs().mean()
        sigma = data[column].std()
        data[column] = data[data[column].abs() < mean+coarseness*sigma][column]


def read_gm_log(filename, colnames=None, index_by_time=True):
    """Make a pandas.DataFrame out of the Dst indeces outputted
    from the GM model log.

    Parameters:
        filename: The filename as a string.
        colnames: Supply the name of the columns whitespace seperated
        index_by_time: Change the index to a time index
    Returns:
        pandas.DataFrame: Of the log file

    Examples:
        # To plot AL and Dst get the log files
        geo = swmfpy.read_gm_log("run/GM/IO2/geoindex_e20140215-100500.log")
        dst = swmfpy.read_gm_log("run/GM/IO2/log_e20140215-100500.log")
        # Then plot using pandas features
        dst["dst_sm"].plot.line()
        geo["AL"].plot.line()
    """
    # If column names were not specified
    if not colnames:
        with open(filename, 'r') as logfile:
            # Usually the names are in the second line
            logfile.readline()
            colnames = logfile.readline().split()
    data = pd.read_fwf(filename, header=None, skiprows=2, names=colnames)
    if index_by_time:
        data.set_index(pd.to_datetime({'year': data['year'],
                                       'month': data['mo'],
                                       'day': data['dy'],
                                       'h': data['hr'],
                                       'm': data['mn'],
                                       's': data['sc']}),
                       inplace=True)
        data.index.names = ['time']
    return data


def trace_fieldline(x, y, u, v, startind=0, **kwags):
    """Returns the traced field line.

    Parameters:
        x: horizontal distances from origin.
        y: vertical distances from origin.
        u: horizontal vector magnitudes.
        v: vertical vector magnitudes.

    Returns:
        xline, yline, uline, vline: The arrays of the traced line
    """
    # First index the variables
    xline = [x[startind]]
    yline = [y[startind]]
    uline = [u[startind]]
    vline = [v[startind]]
    possiblex = [0, 1]
    while possiblex:
        if np.abs(uline[-1]) > np.abs(vline[-1]): # stepping horizontally
            if uline[-1] > 0:
                # step forward
                possiblex = x[np.where(x > xline[-1])]
                possibley = y[np.where(x > xline[-1])]
                possibleu = u[np.where(x > xline[-1])]
                possiblev = v[np.where(x > xline[-1])]
                ydistance = np.abs(possibley - yline[-1])
                possiblex = possiblex[np.where(ydistance == np.min(ydistance))]
                possibley = possibley[np.where(ydistance == np.min(ydistance))]
                possibleu = possibleu[np.where(ydistance == np.min(ydistance))]
                possiblev = possiblev[np.where(ydistance == np.min(ydistance))]
                xline.append(possiblex)
                yline.append(possibley)
                uline.append(possibleu)
                vline.append(possiblev)
            else:
                # step backward
                possiblex = x[np.where(x < xline[-1])]
                possibley = y[np.where(x < xline[-1])]
                possibleu = u[np.where(x < xline[-1])]
                possiblev = v[np.where(x < xline[-1])]
                ydistance = np.abs(possibley - yline[-1])
                possiblex = possiblex[np.where(ydistance == np.min(ydistance))]
                possibley = possibley[np.where(ydistance == np.min(ydistance))]
                possibleu = possibleu[np.where(ydistance == np.min(ydistance))]
                possiblev = possiblev[np.where(ydistance == np.min(ydistance))]
                xline.append(possiblex)
                yline.append(possibley)
                uline.append(possibleu)
                vline.append(possiblev)
        else: # stepping vertically
            if vline[-1] > 0:
                # step forward
                possiblex = x[np.where(y > yline[-1])]
                possibley = y[np.where(y > yline[-1])]
                possibleu = u[np.where(y > yline[-1])]
                possiblev = v[np.where(y > yline[-1])]
                xdistance = np.abs(possiblex - xline[-1])
                possiblex = possiblex[np.where(xdistance == np.min(xdistance))]
                possibley = possibley[np.where(xdistance == np.min(xdistance))]
                possibleu = possibleu[np.where(xdistance == np.min(xdistance))]
                possiblev = possiblev[np.where(xdistance == np.min(xdistance))]
                xline.append(possiblex)
                yline.append(possibley)
                uline.append(possibleu)
                vline.append(possiblev)
            else:
                # step backward
                possiblex = x[np.where(y < yline[-1])]
                possibley = y[np.where(y < yline[-1])]
                possibleu = u[np.where(y < yline[-1])]
                possiblev = v[np.where(y < yline[-1])]
                xdistance = np.abs(possiblex - xline[-1])
                possiblex = possiblex[np.where(xdistance == np.min(xdistance))]
                possibley = possibley[np.where(xdistance == np.min(xdistance))]
                possibleu = possibleu[np.where(xdistance == np.min(xdistance))]
                possiblev = possiblev[np.where(xdistance == np.min(xdistance))]
                xline.append(possiblex)
                yline.append(possibley)
                uline.append(possibleu)
                vline.append(possiblev)
    return (xline, yline, uline, vline)
