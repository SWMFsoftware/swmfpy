"""### Tools to download/upload data on the web

Here are a collection of tools to work with data on the internet. Thus,
this module mostly requires an internet connection. Which on some
supercomputers would be turned off during a job run. In scripts, make sure to
use these to preprocess before submitting jobs.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import datetime as dt
import urllib
from .__init__ import OMNI_COLS
from .tools import _import_error_string, _nearest


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
        **kwargs:
            original_colnames (bool): Use the original column names from the
                                      spdf specification. The alternative is
                                      nicer and shorter names. Defaults to
                                      False.

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

    from dateutil import rrule

    # Set the url
    omni_url = 'https://spdf.gsfc.nasa.gov/pub/data/omni/'
    if kwargs.get('high_res', True):
        omni_url += 'high_res_omni/monthly_1min/'

    # Initialize return dict
    return_data = {}
    return_data['times'] = []
    col_names = []
    for name in OMNI_COLS:
        if kwargs.get('original_colnames', False):
            col_names += [name[0]]
            return_data[name[0]] = []
        else:
            col_names += [name[1]]
            return_data[name[1]] = []

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
                return_data['times'] += [time]
                # Assign the data from after the time columns (0:3)
                for num, value in enumerate(cols[4:len(col_names)+4]):
                    if _check_bad_omni_num(value):
                        return_data[col_names[num]] += [None]
                    else:
                        return_data[col_names[num]] += [float(value)]

    return return_data  # dictionary with omni values where index is the row


def _check_bad_omni_num(value_string):
    """Returns true if bad or false if not. Bad numbers usually just have 9s
       in omni.
    """
    for char in value_string:
        if char not in ('9', '.'):
            return False
    return True


def download_magnetogram_hmi(mag_time, hmi_map='hmi.B_720s', **kwargs):
    """Downloads HMI vector magnetogram fits files.

    This will download vector magnetogram FITS files from
    Joint Science Operations Center (JSOC) near a certain hour.

    This unfortunately depends on sunpy and drms, if you don't have it try,

    ```bash
    pip install -U --user sunpy drms
    ```

    Args:
        mag_time (datetime.datetime): Time after which to find
                                      vector magnetograms.
        hmi_map (str): JSOC prefix for hmi maps. Currently can only do
                       'hmi.B_720s' and 'hmi.b_synoptic.small'.

    **kwargs:
        download_dir (str): Relative directory to download to.
        verbose (bool): (default False) print out the files it's downloading.

    Returns:
        str: list of filenames downloaded.

    Raises:
        ImportError: If module `drms` is not found.
        FileNotFoundError: If the JSOC doesn't have the magnetograms for that
                           time.

    Examples:
        ```python
        from swmfpy.web import download_magnetogram_hmi
        import datetime as dt

        # I am interested in the hmi vector magnetogram from 2014, 2, 18
        time_mag = dt.datetime(2014, 2, 18, 10)  # Around hour 10

        # Calling it will download
        filenames = download_magnetogram_hmi(mag_time=time_mag,
                                             hmi_map='B_720s',
                                             download_dir='mydir/')

        # To see my list
        print('The magnetograms I downloaded are:', filenames)

        # You may call and ignore the file list
        download_magnetogram_hmi(mag_time=time_mag,
                                 hmi_map='b_synoptic_small',
                                 download_dir='mydir')
        ```
    """

    # import drms dynamically
    try:
        import drms
    except ImportError:
        raise ImportError(_import_error_string('drms'))

    get_urls = {
        'hmi.B_720s': _get_urls_hmi_b720,
        'hmi.b_synoptic_small': _get_urls_hmi_b_synoptic_small,
        }
    client = drms.Client()

    urls = get_urls[hmi_map](client, mag_time)

    # Download data
    if kwargs.get('verbose', False):
        print('Starting download of magnetograms:\n')
    return_name = ''
    download_dir = kwargs.get('download_dir', '')
    if not download_dir.endswith('/') and download_dir != '':
        download_dir += '/'
    for data_time, mag_url in urls:
        if mag_url == 'BadSegLink':  # JSOC will return this if not found
            raise FileNotFoundError('Could not find those HMI magnetograms.')
        filename = 'hmi_' + str(data_time).replace(' ', '_')  # Add timestamp
        filename += '_' + mag_url.split('/')[-1]  # Last is filename
        url = 'http://jsoc.stanford.edu' + mag_url
        if kwargs.get('verbose', False):
            print(f'Downloading from {url} to {download_dir+filename}.')
        with urllib.request.urlopen(url) as fits_file:
            with open(download_dir+filename, 'wb') as local_file:
                local_file.write(fits_file.read())
        if kwargs.get('verbose', False):
            print(f'Done writing {download_dir+filename}.\n')
        return_name = download_dir+filename

    if kwargs.get('verbose', False):
        print('Completed downloads.\n')

    return return_name


def _get_urls_hmi_b_synoptic_small(client, mag_time):
    """Returns for #download_magnetogram_hmi needed urls

    Args:
        client (drms.Client): To query and return urls.
        mag_time (datetime.datetime): To find nearest magnetogram.

    Returns:
        generator that yields (datetime.datetime, str): Time of magnetogram,
            suffix url of magnetogram
    """
    try:
        from sunpy.coordinates.sun import carrington_rotation_number
    except ImportError as error:
        print(_import_error_string('sunpy'))
        raise error

    cr_number = int(round(carrington_rotation_number(mag_time)))
    query_string = f'hmi.b_synoptic_small[{int(round(cr_number))}]'
    components = ['Bp', 'Bt', 'Br']
    data = client.query(query_string, seg=components)
    # Generator to find the nearest time
    prefix_str = 'CR' + str(cr_number) + '_' + str(mag_time)
    urls = ((prefix_str, data[component][0]) for component in components)
    return urls


def _get_urls_hmi_b720(client, mag_time):
    """Returns for #download_magnetogram_hmi needed urls for hmi.B_720s

    Args:
        client (drms.Client): To query and return urls.
        mag_time (datetime.datetime): To find nearest magnetogram.

    Returns:
        generator that yields (datetime.datetime, str): Time of magnetogram,
            suffix url of magnetogram
    """
    import drms
    query_string = 'hmi.B_720s'
    query_string += f'[{mag_time.year}.'
    query_string += f'{str(mag_time.month).zfill(2)}.'
    query_string += f'{str(mag_time.day).zfill(2)}_'
    query_string += f'{str(mag_time.hour).zfill(2)}'
    query_string += '/1h]'
    data = client.query(query_string, key='T_REC', seg='field')
    times = drms.to_datetime(data[0].T_REC)
    nearest_time = _nearest(mag_time, times)
    # Generator to find the nearest time
    urls = ((data_time, mag_url) for (data_time, mag_url)
            in zip(times, data[1].field) if data_time == nearest_time)
    return urls


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
    return_names = filenames
    for index, filename in enumerate(return_names):
        if '.gz' in filename:
            return_names[index] = filename.replace('.gz', '')
    return return_names
