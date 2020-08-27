"""### Input/Output tools

Here are tools to read and write files relating to SWMF.
"""

import datetime as dt
import warnings
import numpy as np
from .tools import _make_line


def write_imf_input(imf_data, filename='IMF.dat', **kwargs):
    """Creates the IMF.dat input file for the SWMF BATS-R-US geospace model.

    `imf_data` must be a dictionary of array_like objects with same length
    in data. In swmfpy Pythonic versions are always preferred so the 'times'
    must be `datetime.datetime` array.
    imf_data = dict(times, bx, by, bz, vx, vy, vz, density, temperature)

    Args:
        imf_data (dict): This dictionary contains the solar wind data.
        filename (str): (default: 'IMF.dat') Filename to write to.
        **kwargs:
            commands ([str]): (default: None) List of commands to write to imf
                              input file (indexed by line then by tabs on same
                              line). *Note*: Must be a list if have one command
                              str.

    Raises:
        TypeError: If commands is not a list or tuple. It must be at least a
                   one element list of strings.
        AssertionError: If inputs aren't prepared properly (key names)

    Examples:
        ```python
        from swmfpy.io import write_imf_input

        # Prepare imf dictionary: imf_data
        write_imf_input(imf_data, filename='run/IMF.dat')
        ```
    """

    columns_dat = ['year', 'month', 'day', 'hour', 'min', 'sec', 'msec',
                   'bx', 'by', 'bz', 'vx', 'vy', 'vz',
                   'density', 'temperature']
    column_keys = ['times',
                   'bx', 'by', 'bz', 'vx', 'vy', 'vz',
                   'density', 'temperature']
    if kwargs.get('column_keys', None):
        column_keys = kwargs.get('column_keys', column_keys)

    def _time_repr(time_raw):
        'Represent time in a suitable format'
        raw_str = dt.datetime.strftime(time_raw, '%Y %m %d %H %M %S %f')[:-3]
        return raw_str.split()

    with open(filename, 'w') as file_imf:
        # header
        file_imf.write('Made with swmfpy ')
        file_imf.write('(https://gitlab.umich.edu/swmf_software/swmfpy)\n\n')

        # write commands
        commands = kwargs.get('commands', None)
        if commands:
            try:
                isinstance(commands, (list, tuple))
            except TypeError:
                raise TypeError(f'{__name__}: commands must be list or tuple')
            for command in commands:
                file_imf.write(_make_line(command)+'\n')

        # write dat file
        file_imf.write('\n'+' '.join(_justified(columns_dat)))
        file_imf.write('\n#START\n')
        lines = []
        for index, _time in enumerate(imf_data[column_keys[0]]):
            dirty = False  # Don't write line if it has NaN
            line = _time_repr(_time)
            for key in column_keys[1:]:
                line += [str(round(imf_data[key][index], 2))]
                if np.isnan(imf_data[key][index]):
                    dirty = True
            if not dirty:
                line = ' '.join(_justified(line))
                lines += line + '\n'
        file_imf.writelines(lines)


def _justified(str_list, width=7):
    'Returns justified list from string list'
    return [s.rjust(width) for s in str_list]


def read_wdc_ae(wdc_filename):
    """Read an auroral electrojet (AE) indeces from Kyoto's World Data Center
       text file into a dictionary of lists.

    Args:

        wdc_filename (str): Filename of wdc data from
                            http://wdc.kugi.kyoto-u.ac.jp/
    Returns:
        dict: Auroral indeces 'AL', 'AE', 'AO', 'AU'
            datetime.datetime: 'times'
            int: 'values'
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
        dict: of values. {'[ASY-SYM]-[D-H]': 'times': [], 'values': []}

    Examples:
        ```python
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


def _coarse_filtering(data, coarseness=3):
    """Applies coarse filtering to a pandas.DataFrame"""
    for column in data.columns:
        mean = data[column].abs().mean()
        sigma = data[column].std()
        data[column] = data[data[column].abs() < mean+coarseness*sigma][column]


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
        dict: Dictionary of the log file

    Examples:
        To plot AL and Dst get the log files
        ```python
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
        try:
            colnames = _fix_str_duplicates(colnames)
        except RuntimeWarning:
            print(f'{__name__}: Warning: '
                  + 'Found duplicates in column names. '
                  + 'Changes made to column names.')
        for col in colnames:
            return_data[col] = []

        # Fill data dictionary
        for line_num, line in enumerate(logfile):
            if line_num > 2:  # First two lines are usually metadata
                for col, data in enumerate(line.strip().split()):
                    if dtypes:
                        data = dtypes[col](data)
                    else:
                        try:
                            data = float(data)
                        except ValueError as err:
                            data = np.nan
                            warnings.warn('Value error and no manual dtype set'
                                          + ' changing to NaN',
                                          RuntimeWarning)
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


def _fix_str_duplicates(str_list):
    """Returns a list and bool if a fix was made.
       The fix is adding an _[index] to avoid duplicates.
    """
    duplicate_found = False
    for index, string in enumerate(str_list):
        if str_list.count(string) > 1:
            duplicate_found = True
            str_list[index] = string + f'_{index}'
    if duplicate_found:
        raise RuntimeWarning
    return str_list
