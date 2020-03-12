"""Input/Output tools

Input/Output
============

Here are tools to read and write files relating to SWMF.

TODO: Move pandas dependancy elsewhere.
"""

import datetime as dt
import numpy as np


def read_wdc_ae(wdc_filename):
    """Read an auroral electrojet (AE) indeces from Kyoto's World Data Center
       text file into a dictionary of lists.

    Args:
        wdc_filename (str): Filename of wdc data from
                            http://wdc.kugi.kyoto-u.ac.jp/
    Returns:
        dict: {"time" (datetime.datetime): list of datetime objects
                                           corresponding to time in UT.
               "AL", "AE", "AO", "AU" (int): Auroral indeces.
              }
    """
    data = {'AL': {'Time': [], 'Index': []},
            'AE': {'Time': [], 'Index': []},
            'AO': {'Time': [], 'Index': []},
            'AU': {'Time': [], 'Index': []}}
    with open(wdc_filename) as wdc_file:
        for line in wdc_file:
            ind_data = line.split()
            for minute in range(60):
                # TODO: Use .zfill()?
                str_min = str(minute)
                if minute < 10:
                    str_min = '0' + str_min
                time = dt.datetime.strptime(ind_data[1][:-5]
                                            + ind_data[1][7:-2]
                                            + str_min,
                                            '%y%m%d%H%M')
                data[ind_data[1][-2:]]['Time'] += [time]
                data[ind_data[1][-2:]]['Index'] += [int(ind_data[3+minute])]
    return data


def read_wdc_asy_sym(wdc_filename):
    """Docstring
    """

    return_data = {'ASY': {'Time': [], 'Index': []},
                   'SYM': {'Time': [], 'Index': []}}

    with open(wdc_filename) as wdc_file:
        header = wdc_file.readline()[:6]
        assert header == 'ASYSYM', ('File does not seem to be'
                                    + 'an ASY/SYM file from wdc.'
                                    + 'First six characters: '
                                    + header)
        for line in wdc_file:
            data = line.split()

    return_data


def read_omni_csv(filename, filtering=False, **kwargs):
    """Take an OMNI csv file from cdaweb.sci.gsfc.nasa.gov
    and turn it into a pandas.DataFrame.

    Args:
        fnames (dict): dict with filenames from omni .lst files.
                       The keys must be: density, temperature,
                                         magnetic_field, velocity
        filtering (bool): default=False Remove points where the value
                          is >sigma (default: sigma=3) from mean.
        **kwargs:
            coarseness (int): default=3, Number of standard deviations
                              above which to remove if filtering=True.
            clean (bool): default=True, Clean the omni data of bad data points

    Returns:
        pandas.DataFrame: object with solar wind data

    Make sure to download the csv files with cdaweb.sci.gsfc.nasa.gov
    the header seperated into a json file for safety.

    This only tested with OMNI data specifically.


    """
    import pandas as pd
    # Read the csv files and set the index to dates
    colnames = ['Time', 'Bx [nT]', 'By [nT]', 'Bz [nT]',
                'Vx [km/s]', 'Vy [km/s]', 'Vz [km/s]',
                'Rho [n/cc]', 'T [K]']
    with open(filename, 'r') as datafile:
        data = pd.read_csv(datafile, names=colnames, skiprows=1)
    data.set_index(pd.to_datetime(data[data.columns[0]]), inplace=True)
    data.drop(columns=data.columns[0], inplace=True)
    data.index.name = "Time [UT]"

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
        _coarse_filtering(data, kwargs.get('coarseness', 3))
    return data.interpolate().bfill().ffill()


def _coarse_filtering(data, coarseness=3):
    """Applies coarse filtering to a pandas.DataFrame"""
    for column in data.columns:
        mean = data[column].abs().mean()
        sigma = data[column].std()
        data[column] = data[data[column].abs() < mean+coarseness*sigma][column]


def write_imf_input(data, outfilename="IMF.dat", enable_rb=True, **kwargs):
    """Writes the pandas.DataFrame into an input file
    that SWMF can read as input IMF (IMF.dat).

    Args:
        data: pandas.DataFrame object with solar wind data
        outfilename: The output file name for ballistic solar wind data.
                     (default: "IMF.dat")
        enable_rb: Enables solar wind input for the radiation belt model.
                   (default: True)

    Other paramaters:
        gse: (default=False)
            Use GSE coordinate system for the file instead of GSM default.
    """

    # Generate BATS-R-US solar wind input file
    with open(outfilename, 'w') as outfile:
        outfile.write("CSV files downloaded from ")
        outfile.write("https://cdaweb.gsfc.nasa.gov/\n")
        if kwargs.get('gse', False):
            outfile.write("#COOR\nGSE\n")
        outfile.write("yr mn dy hr min sec msec bx by bz vx vy vz dens temp\n")
        outfile.write("#START\n")
        for index, rows in data.iterrows():
            outfile.write(index.strftime("%Y %m %d %H %M %S") + ' ')
            outfile.write(index.strftime("%f")[:3] + ' ')
            outfile.write(str(rows['Bx [nT]'])[:7] + ' ')
            outfile.write(str(rows['By [nT]'])[:7] + ' ')
            outfile.write(str(rows['Bz [nT]'])[:7] + ' ')
            outfile.write(str(rows['Vx [km/s]'])[:7] + ' ')
            outfile.write(str(rows['Vy [km/s]'])[:7] + ' ')
            outfile.write(str(rows['Vz [km/s]'])[:7] + ' ')
            outfile.write(str(rows['Rho [n/cc]'])[:7] + ' ')
            outfile.write(str(rows['T [K]'])[:7] + ' ')
            outfile.write('\n')
    # Generate RBE model solar wind input file
    if enable_rb:
        with open("RB.SWIMF", 'w') as rbfile:
            # Choose first element as t=0 header (unsure if this is safe)
            rbfile.write(data.index[0].strftime("%Y, %j, %H ")
                         + "! iyear, iday, ihour corresponding to t=0\n")
            swlag_time = None
            if swlag_time in kwargs:
                rbfile.write(str(kwargs["swlag_time"]) + "  "
                             + "! swlag time in seconds "
                             + "for sw travel to subsolar\n")
            # Unsure what 11902 means but following example file
            rbfile.write("11902 data                   "
                         + "P+ NP NONLIN    P+ V (MOM)\n")
            # Quantity header
            rbfile.write("dd mm yyyy hh mm ss.ms           "
                         + "#/cc          km/s\n")
            for index, rows in data.iterrows():
                rbfile.write(index.strftime("%d %m %Y %H %M %S.%f")
                             + "     "
                             + str(rows['Rho [n/cc]'])[:8]
                             + "     "
                             # Speed magnitude
                             + str(np.sqrt(rows['Vx [km/s]']**2
                                           + rows['Vy [km/s]']**2
                                           + rows['Vz [km/s]']**2))[:8]
                             + '\n')


def read_gm_log(filename, colnames=None, index_time=True):
    """Make a dictionary out of the indeces outputted
    from the GM model log.

    Args:
        filename (str): The filename as a string.
        colnames ([str]): (default: None) Supply the name of the columns.
                                          If None it will use second line
                                          of log file.
        index_time (bool): (default: True) Make a column of dt.datetime objects
                                           in dictionary key 'Time [UT]'.

    Returns:
        Dictionary of the log file

    Examples:
        To plot AL and Dst get the log files
        ```
        geo = swmfpy.io.read_gm_log('run/GM/IO2/geoindex_e20140215-100500.log')
        dst = swmfpy.io.read_gm_log('run/GM/IO2/log_e20140215-100500.log')

        # Plot AL indeces
        plt.plot(geo['Time [UT]', geo['AL'])
        ```

    """

    # If column names were not specified
    return_data = {}
    with open(filename, 'r') as logfile:

        # Find column names and initialize
        description = logfile.readline()
        return_data['description'] = description
        # Usually the names are in the second line
        if not colnames:
            colnames = logfile.readline().split()
        for col in colnames:
            return_data[col] = []

        # Fill data dictionary
        for line_num, line in enumerate(logfile):
            if line_num > 2:  # First two lines are usually metadata
                for col, data in enumerate(line.split()):
                    return_data[colnames[col]].append(data)

        # datetime index
        if index_time:
            return_data['Time [UT]'] = []
            for row, year in enumerate(return_data[colnames[1]]):
                return_data['Time [UT]'].append(
                    dt.datetime(int(year),
                                int(return_data[colnames[2]][row]),  # month
                                int(return_data[colnames[3]][row]),  # day
                                int(return_data[colnames[4]][row]),  # hour
                                int(return_data[colnames[5]][row]),  # min
                                int(return_data[colnames[6]][row]),  # sec
                                int(return_data[colnames[7]][row])))  # ms

    return return_data
