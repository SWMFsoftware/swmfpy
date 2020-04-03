"""Tools to retrieve and send data on the web.

Here are a collection of tools to work with data on the internet. Thus,
this module mostly requires an internet connection.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import datetime as dt


def get_omni_data(time_from, time_to, **kwargs):
    """Retrieve omni solar wind data over http.

    This will download omni data from https://spdf.gsfc.nasa.gov/pub/data/omni
    and put it into a dictionary. If your data is large, then make a csv and
    use swmfpy.io.read_omni_data().

    Args:
        time_from (datetime.datetime): The start time of the solar wind
                                       data that you want to receive.
        time_to (datetime.datetime): The end time of the solar wind data
                                     you want to receive.

    Returns:
        dict: This will be a list of *all* columns
              available in the omni data set.

    Examples:
        ```python
        import datetime
        import swmfpy.web

        storm_start = datetime.datetime(year=2000, month=1, day=1)
        storm_end = datetime.datetime(year=2000, month=2, day=15)
        data = swmfpy.web.get_omni_data(time_from=storm_start,
                                        time_to=storm_end)
        ```
    """
    # Author: Qusai Al Shidi
    # Email: qusai@umich.edu

    import urllib.request
    from dateutil import rrule

    # This is straight from the format guide on spdf
    col_names = ('ID for IMF spacecraft',
                 'ID for SW Plasma spacecraft',
                 '# of points in IMF averages',
                 '# of points in Plasma averages',
                 'Percent interp',
                 'Timeshift, sec',
                 'RMS, Timeshift',
                 'RMS, Phase front normal',
                 'Time btwn observations, sec',
                 'Field magnitude average, nT',
                 'Bx, nT (GSE, GSM)',
                 'By, nT (GSE)',
                 'Bz, nT (GSE)',
                 'By, nT (GSM)',
                 'Bz, nT (GSM)',
                 'RMS SD B scalar, nT',
                 'RMS SD field vector, nT',
                 'Flow speed, km/s',
                 'Vx Velocity, km/s, GSE',
                 'Vy Velocity, km/s, GSE',
                 'Vz Velocity, km/s, GSE',
                 'Proton Density, n/cc',
                 'Temperature, K',
                 'Flow pressure, nPa',
                 'Electric field, mV/m',
                 'Plasma beta',
                 'Alfven mach number',
                 'X(s/c), GSE, Re',
                 'Y(s/c), GSE, Re',
                 'Z(s/c), GSE, Re',
                 'BSN location, Xgse, Re',
                 'BSN location, Ygse, Re',
                 'BSN location, Zgse, Re',
                 'AE-index, nT',
                 'AL-index, nT',
                 'AU-index, nT',
                 'SYM/D index, nT',
                 'SYM/H index, nT',
                 'ASY/D index, nT',
                 'ASY/H index, nT',
                 'PC(N) index',
                 'Magnetosonic mach number')

    # Set the url
    omni_url = 'https://spdf.gsfc.nasa.gov/pub/data/omni/'
    if kwargs.get('high_res', True):
        omni_url += 'high_res_omni/monthly_1min/'

    # Initialize return dict
    return_data = {}
    return_data['times'] = []
    for name in col_names:
        return_data[name] = []

    # Iterate monthly to save RAM
    for date in rrule.rrule(rrule.MONTHLY,
                            dtstart=dt.datetime(time_from.year,
                                                time_from.month,
                                                1),
                            until=dt.datetime(time_to.year,
                                              time_to.month,
                                              25)):
        suffix = 'omni_min'
        suffix += str(date.year) + str(date.month).zfill(2)
        suffix += '.asc'
        omni_data = list(urllib.request.urlopen(omni_url+suffix))

        # Parse omni data
        for line in omni_data:
            cols = line.decode('ascii').split()
            # Time uses day of year which must be parsed
            time = dt.datetime.strptime(cols[0] + ' '  # year
                                        + cols[1] + ' '  # day of year
                                        + cols[2] + ' '  # hour
                                        + cols[3],  # minute
                                        '%Y %j %H %M')
            if time >= time_from and time <= time_to:
                return_data['times'].append(time)
                # Assign the data from after the time columns (0:3)
                for num, value in enumerate(cols[4:len(col_names)+4]):
                    if _check_bad_omni_num(value):
                        return_data[col_names[num]].append(None)
                    else:
                        return_data[col_names[num]].append(float(value))

    return return_data  # dictionary with omni values where index is the row


def _check_bad_omni_num(value_string):
    """Returns true if bad or false if not"""
    for char in value_string:
        if char != '9' and char != '.':
            return False
    return True


def download_magnetogram_adapt(time, map_type='fixed', **kwargs):
    """This routine downloads GONG ADAPT magnetograms.

    Downloads ADAPT magnetograms from ftp://gong2.nso.edu/adapt/maps/gong/
    to a local directory. It will download all maps with the regex file
    pattern: adapt4[0,1]3*yyyymmddhh

    Args:
        time (datetime.datetime): Time in which you want the magnetogram.
        map_type (str): (default: 'fixed')
                        Choose either 'fixed' or 'central' for
                        the map type you want.
        **kwargs:
            download_dir (str): (default is current dir) Relative directory
                                where you want the maps to be downloaded.

    Returns:
        str: First unzipped filename found.

    Raises:
        NotADirectoryError: If the adapt maps directory
                            is not found on the server.
        ValueError: If map_type is not recognized.
                    (i.e. not 'fixed' or 'central')
        FileNotFoundError: If maps were not found.

    Examples:
        ```python
        import datetime as dt

        # Use datetime objects for the time
        time_flare = dt.datetime(2018, 2, 12, hour=10)
        swmfpy.web.download_magnetogram_adapt(time=time_flare,
                                              map_type='central',
                                              download_dir='./mymaps/')
        ```
    """
    # Author: Zhenguang Huang
    # Email: zghuang@umich.edu

    import ftplib
    from ftplib import FTP
    import gzip
    import shutil

    if map_type == 'fixed':
        map_id = '0'
    elif map_type == 'central':
        map_id = '1'
    else:
        raise ValueError('Not recognized type of ADAPT map')

    # Go to the the ADAPT ftp server
    ftp = FTP('gong2.nso.edu')
    ftp.login()

    # Only ADAPT GONG is considered
    ftp.cwd('adapt/maps/gong')

    # Go to the specific year
    try:
        ftp.cwd(str(time.year))
    except ftplib.all_errors:
        ftp.quit()
        raise NotADirectoryError('Cannot go to the specific year directory')

    # ADAPT maps only contains the hours for even numbers
    if time.hour % 2 != 0:
        print('Warning: Hour must be an even number.',
              'The entered hour value is changed to',
              time.hour//2*2)
    # Only consider the public (4) Carrington Fixed (0) GONG (3) ADAPT maps
    file_pattern = 'adapt4' + map_id + '3*' \
        + str(time.year).zfill(4) \
        + str(time.month).zfill(2) \
        + str(time.day).zfill(2) \
        + str(time.hour//2*2).zfill(2) + '*'
    # adapt4[0,1]3*yyyymmddhh

    filenames = ftp.nlst(file_pattern)

    if len(filenames) < 1:
        raise FileNotFoundError('Could not find a file that matches'
                                + 'the pattern.')

    for filename in filenames:
        # open the file locally
        directory = kwargs.get('download_dir', './')
        if directory[-1] != '/':
            directory += '/'
        with open(directory + filename, 'wb') as fhandle:
            # try to download the magnetogram
            try:
                ftp.retrbinary('RETR ' + filename, fhandle.write)
            except ftplib.all_errors:
                ftp.quit()
                raise FileNotFoundError('Cannot download ', filename)

        # unzip the file
        if '.gz' in filename:
            filename_unzip = filename.replace('.gz', '')
            with gzip.open(directory + filename, 'rb') as s_file:
                with open(directory + filename_unzip, 'wb') as d_file:
                    shutil.copyfileobj(s_file, d_file, 65536)

    # close the connection
    ftp.quit()

    # return first file name if all goes well
    return_name = filenames[0]
    if '.gz' in return_name:
        return_name = return_name[:-3]
    return return_name
