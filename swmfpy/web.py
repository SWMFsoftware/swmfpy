"""Tools to retrieve and send data on the web.

SWMF Web Tools (swmfpy.web)
===========

Here are a collection of tools to work with data on the internet. Thus,
this module mostly requires an internet connection.
"""
__author__ = 'Qusai Al Shidi'
__email__ = 'qusai@umich.edu'

import urllib.request
import datetime as dt
from dateutil import rrule


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
    return_data['Time [UT]'] = []
    for name in col_names:
        return_data[name] = []

    # Iterate monthly to save RAM
    for date in rrule.rrule(rrule.MONTHLY, dtstart=time_from, until=time_to):
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
                return_data['Time [UT]'].append(time)
                # Assign the data from after the time columns (0:3)
                for num, value in enumerate(cols[4:len(col_names)+4]):
                    return_data[col_names[num]].append(float(value))

    return return_data  # dictionary with omni values where index is the row
