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
        dict: {
               Auroral indeces 'AL', 'AE', 'AO', 'AU' (int): {
                    'times' (datetime.datetime): List of datetime objects
                                                 corresponding to time in UT.
                    'values' (int): List of indeces.
              }
    """

    # Initialize return data
    return_data = {'AL': {'times': [], 'values': []},
                   'AE': {'times': [], 'values': []},
                   'AO': {'times': [], 'values': []},
                   'AU': {'times': [], 'values': []}}

    # Open and make sure it is correct file
    with open(wdc_filename, 'rt') as wdc_file:
        header = wdc_file.readline()
        assert header[:8] == 'AEALAOAU', \
            'Does not seem to be a WDC AE file. First 8 chars: ' + header[:8]

        # Parse
        for line in wdc_file:
            data = line.split()
            year_suffix = int(data[1][:2])
            if year_suffix < 50:
                year = 2000 + year_suffix
            else:
                year = 1990 + year_suffix
            month = int(data[1][2:4])
            day = int(data[1][4:6])
            hour = int(data[1][7:9])
            index = data[1][-2:]
            values_60 = [int(val) for val in data[3:60+3]]

            # Fill
            for minute, value in enumerate(values_60):
                return_data[index]['values'].append(value)
                return_data[index]['times'].append(
                    dt.datetime(year, month, day, hour, minute))

    return return_data


def read_wdc_asy_sym(wdc_filename):
    """Reads a WDC file for ASY/SYM data.

    Reads an ASY/SYM file downloaded from
    http://wdc.kugi.kyoto-u.ac.jp/aeasy/index.html
    and puts it into a dictionary.

    Args:
        wdc_filename (str): Relative filename (or file handle no.) to read.

    Returns:
        dict: of values.
        {'[ASY-SYM]-[D-H]': 'times': [], 'values': []}

    Examples:
        ```
        indeces = swmfpy.io.read_wdc_asy_sym('wdc.dat')
        # Plot data
        plt.plot(indeces['SYM-H']['times'],
                 indeces['SYM-H']['values'],
                 label='SYM-H [nT]'
                 )
        plt.xlabel('Time [UT]')
        ```

    Important to note if there is bad data it will be filled as None.
    """

    return_data = {
        'ASY-D': {
            'times': [],
            'values': [],
            },
        'ASY-H': {
            'times': [],
            'values': [],
            },
        'SYM-D': {
            'times': [],
            'values': [],
            },
        'SYM-H': {
            'times': [],
            'values': []
            }
        }

    with open(wdc_filename) as wdc_file:
        # Check for correct file
        header = wdc_file.readline()
        assert header[:12] == 'ASYSYM N6E01', ('File does not seem to be'
                                               + 'an ASY/SYM file from wdc.'
                                               + 'First 12 characters: '
                                               + header)
        return_data['edition'] = header[24:34]

        for line in wdc_file:
            # Parse
            year = int(line[12:14])
            if year < 70:  # Starts from 1970 but only gives 2 digits
                year += 2000
            else:
                year += 1900
            month = int(line[14:16])
            day = int(line[16:18])
            hour = int(line[19:21])
            comp = line[18]
            index = line[21:24]

            # Fill 60 min data
            data = line.split()
            values_60 = [int(val) for val in data[2:62]]
            for minute, value in enumerate(values_60):
                return_data[index+'-'+comp]['times'].append(
                    dt.datetime(year, month, day, hour, minute))
                # Check if data is bad
                if value != 99999:
                    return_data[index+'-'+comp]['values'].append(
                        value)
                else:
                    return_data[index+'-'+comp]['values'].append(
                        None)

    return return_data


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
    # TODO: This needs a lot of work

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


def read_gm_log(filename, colnames=None, dtypes=None, index_time=True):
    """Make a dictionary out of the indeces outputted
    from the GM model log.

    Args:
        filename (str): The relative filename as a string. (or file handle no.)
        colnames ([str]): (default: None) Supply the name of the columns.
                                          If None it will use second line
                                          of log file.
        dtypes ([types]): (default: None) Provide types for the columns, if
                                          None then all will be float.
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
        plt.plot(geo['times', geo['AL'])
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
                    if dtypes:
                        data = dtypes[col](data)
                    else:
                        data = float(data)
                    return_data[colnames[col]].append(data)

        # datetime index
        if index_time:
            return_data['times'] = []
            for row, year in enumerate(return_data[colnames[1]]):
                return_data['times'].append(
                    dt.datetime(int(year),
                                int(return_data[colnames[2]][row]),  # month
                                int(return_data[colnames[3]][row]),  # day
                                int(return_data[colnames[4]][row]),  # hour
                                int(return_data[colnames[5]][row]),  # min
                                int(return_data[colnames[6]][row]),  # sec
                                int(return_data[colnames[7]][row])))  # ms

    return return_data
