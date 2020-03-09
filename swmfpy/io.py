"""Input/Output tools

Input/Output
============

Here are tools to read and write files relating to SWMF.

TODO: Move pandas dependancy elsewhere.
"""

import os
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
    data = {"AL": {"Time": [], "Index": []},
            "AE": {"Time": [], "Index": []},
            "AO": {"Time": [], "Index": []},
            "AU": {"Time": [], "Index": []}}
    with open(wdc_filename) as wdc_file:
        for line in wdc_file:
            ind_data = line.split()
            for minute in range(60):
                str_min = str(minute)
                if minute < 10:
                    str_min = "0" + str_min
                time = dt.datetime.strptime(ind_data[1][:-5]
                                            + ind_data[1][7:-2]
                                            + str_min,
                                            "%y%m%d%H%M")
                data[ind_data[1][-2:]]["Time"] += [time]
                data[ind_data[1][-2:]]["Index"] += [int(ind_data[3+minute])]
    return data


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


def read_gm_log(filename, colnames=None, index_by_time=True):
    """Make a pandas.DataFrame out of the Dst indeces outputted
    from the GM model log.

    Args:
        filename (str): The filename as a string.
        colnames ([str]): Supply the name of the columns
        index_by_time (bool): Change the index to a time index
    Returns:
        pandas.DataFrame of the log file

    Examples:
        To plot AL and Dst get the log files
        ```
        geo = swmfpy.read_gm_log("run/GM/IO2/geoindex_e20140215-100500.log")
        dst = swmfpy.read_gm_log("run/GM/IO2/log_e20140215-100500.log")
        ```

        Then plot using pandas features
        ```
        dst["dst_sm"].plot.line()
        geo["AL"].plot.line()
        ```
    """

    import pandas as pd

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
        data.index.names = ['Time [UT]']
    return data


def _smooth_magnetogram(num_long, num_lat, num_smooth, br_c):
    # Function to smooth magnetogram if needed.

    num_smooth2 = num_smooth//2
    coef = 1./(num_smooth*num_smooth)
    br_orig_g = np.zeros([num_lat, num_long+2*num_smooth2])
    for i_lat in np.arange(num_lat):
        br_orig_g[i_lat, :] = np.hstack((
            br_c[i_lat, num_long-num_smooth2:num_long],
            br_c[i_lat, :], br_c[i_lat, 0:num_smooth2]))
    br_c = np.zeros([num_lat, num_long])
    for i_lat in np.arange(num_lat):
        for i_long in np.arange(num_long):
            for i_sub_lat in np.arange(num_smooth):
                i_lat_ext = i_lat + i_sub_lat - num_smooth2
                i_lat_ext = max([-i_lat_ext-1,
                                 min([i_lat_ext, 2*num_lat-1-i_lat_ext])])
                br_c[i_lat, i_long] += np.sum(
                    br_orig_g[i_lat_ext, i_long:i_long+num_smooth])
            br_c[i_lat, i_long] *= coef
    return br_c


def convert_magnetogram_fits(file_name, type_out, num_smooth, b_max):
    """
    file_name - FITS file containing original magnetogram (include path)
    """

    from astropy.io import fits

    type_mag = 'unknown'
    fits_data = fits.open(file_name)
    try:
        telescope_name = fits_data[0].header['TELESCOP']  # works for MDI, GONG
    except KeyError:
        telescope_name = 'unknown'

    num_long = fits_data[0].header['NAXIS1']  # number of longitude points
    num_lat = fits_data[0].header['NAXIS2']   # latitude
    br_c = fits_data[0].data

    if telescope_name.find('NSO-GONG') > -1:
        type_mag = 'GONG Synoptic'
        try:
            long0 = fits_data[0].header['LONG0']
            if float(long0) > 0.:
                type_mag = 'GONG Hourly'
        except KeyError:
            long0 = - 1

    try:
        cr_number = fits_data[0].header['CAR_ROT']  # for newer magnetograms
    except KeyError:
        cr_number = fits_data[0].header['CARROT']  # for older magnetograms

    if type_mag.find('GONG') > -1:
        map_dat = fits_data[0].header['DATE']  # works for GONG
    b_unit = fits_data[0].header['BUNIT']  # works on GONG, MDI

    fits_data.close()

    if type_mag == 'unknown':
        raise ValueError("I don't recognize the type of this magnetogram.")

    print("This is a", type_mag, "magnetogram on a",
          str(num_long), "X", str(num_lat),
          "  Phi X sin(Theta) grid.")
    if (long0 > 0):  # The date is not informative for an integral synoptic map
        print("Magnetogram Date=", map_dat)

    # Uniform in sinum_lat and longitude grid
    lat_sin_i = np.arcsin(np.linspace(-1. + 1./num_lat, 1. - 1./num_lat,
                                      num_lat))
    long_i = 2.*np.pi*np.linspace(0.5/num_long, 1. - 0.5/num_long, num_long)
    long_earth = -1
    if long0 > 0:
        if any(Type == 'old' for Type in type_out):
            file_id = open('CR_Long.txt', 'w')
            file_id.write("%4d \n" % (cr_number))
            file_id.write("%03d \n" % (long0))
            file_id.close()
        long_earth = long0 + 60

    elif os.path.isfile('Date.in'):
        file_id = open('Date.in', 'r')
        cr_check = int(file_id.readline())
        if (cr_check != cr_number):
            ValueError("The Date.in is within CR"+str(cr_check),
                       "The synoptic map is for CR"+str(cr_number))
        long_earth = int(file_id.readline())
        file_id.close()
    # Conservative smoothing. Boundary condition:
    # Periodic in Longitude, reflect in Latitude.
    if num_smooth > 2:
        br_c = _smooth_magnetogram(num_long, num_lat, num_smooth, br_c)
    if (any(Type == 'old' for Type in type_out)):
        file_id = open('fitsfile.dat', 'w')

        file_id.write('#nMax\n')
        file_id.write(str(180) + '\n')
        file_id.write('#ARRAYSIZE\n')
        file_id.write(str(num_long) + '\n')
        file_id.write(str(num_lat) + '\n')
        file_id.write('#START\n')
        for k in np.arange(num_lat):
            for l in np.arange(num_long):
                file_id.write("%14.6e\n" % br_c[k, l])
        file_id.close()
    if any(Type == 'new' for Type in type_out):
        file_id = open('fitsfile.out', 'w')

        file_id.write('sin(lat) grid,', type_mag, ', map_dat =', map_dat,
                      ', Br['+b_unit+']', '\n')
        file_id.write('       0      0.00000       2       2       1 \n')
        file_id.write('      '+str(num_long)+'     '+str(num_lat)+'\n')
        file_id.write(str(long0)+'     '+str(long_earth)+'\n')
        file_id.write('Longitude Latitude Br long0 long_earth \n')

        for k in np.arange(num_lat):
            for l in np.arange(num_long):
                file_id.write("{0:6.1f}  {1:14.6e} {2:14.6e}\n".format(
                        long_i[l]*(180./np.pi), lat_sin_i[k]*(180./np.pi),
                        max([-b_max, min([b_max, br_c[k, l]])])))
        file_id.close()
    num_param = 2
    param_i = np.zeros(num_param)
    param_i[0] = long0
    param_i[1] = long_earth
    return(num_long, num_lat, num_param, param_i, long_i, lat_sin_i, br_c)


def _remap(num_long, num_lat, num_param,
           param_i, long_i, lat_sin_i,
           br_c, b_max):
    long0 = param_i[0]
    long_earth = param_i[1]
    BrTransp_C = np.transpose(br_c)
    #
    # Centers of the bins for uniform latitude grid:
    #
    lat_uniform_i = np.linspace(-np.pi/2 + np.pi/2/num_lat,
                                np.pi/2 - np.pi/2/num_lat,
                                num_lat)

    # Bin boundaries for uniform latitude grid:
    #
    # boundaries of latitude grid
    BinBound_I = np.linspace(-np.pi/2, np.pi/2, num_lat+1)
    #
    # We will linearly interpolate Br*cos(Latitude) given at sin(theta) grid
    # and integrate it over BinBound_I[l];BinBound_I[l+1] bin. The nodes in
    # which the magnetic field is used for the lth bin have indexes
    # lMin_I[l] till lMax_I[l]. Construct lMin_I and lMax_I
    #
    lMin_I = np.arange(num_lat)
    lMax_I = np.arange(num_lat)
    lMin_I[0] = 0
    lMax_I[0] = lMin_I[0]
    while lat_sin_i[lMax_I[0]] < BinBound_I[1]:
        lMax_I[0] = lMax_I[0] + 1
    for l in np.arange(1, num_lat+1):
        lMin_I[l] = lMin_I[l-1]
        if (lMin_I[l] < num_lat-1):
            while (BinBound_I[l] > lat_sin_i[lMin_I[l]+1]):
                lMin_I[l] = lMin_I[l]+1
                if (lMin_I[l] == num_lat-1):
                    break
        lMax_I[l] = lMin_I[l]
        if (lMin_I[l] < num_lat-1):
            while (BinBound_I[l+1] > lat_sin_i[lMax_I[l]]):
                lMax_I[l] = lMax_I[l]+1
                if (lMax_I[l] == num_lat-1):
                    break
    #
    # Now, construct interpolation weights
    #
    CosLat_I = np.cos(lat_sin_i)
    SinBinBound_I = np.sin(BinBound_I)
    Weight_II = np.zeros([num_lat, num_lat])
    for l in np.arange(num_lat):
        if lMax_I[l] == 0 and lMin_I[l] == 0:  # BB_I[l+1] < LS_I[0]
            Weight_II[l, 0] = CosLat_I[0]*(BinBound_I[l+1]-BinBound_I[l])*(
                (BinBound_I[l+1]+BinBound_I[l])/2-BinBound_I[0])/(
                lat_sin_i[0]-BinBound_I[0])
        # BB_I[l] > LS_I[num_lat-1]
        elif lMax_I[l] == num_lat-1 and lMin_I[l] == num_lat-1:
            Weight_II[l, 0] = CosLat_I[num_lat-1]*(
                BinBound_I[l+1]-BinBound_I[l])*(
                BinBound_I[num_lat] - (BinBound_I[l+1]+BinBound_I[l])/2)/(
                BinBound_I[num_lat] - lat_sin_i[num_lat-1])
        # BB_I[l] < LS_U[0] < BB_I[l+1] < LS_I[1]
        elif lat_sin_i[0] > BinBound_I[l]:
            Weight_II[l, 0] = ((lat_sin_i[0]-BinBound_I[l])*(
                    (lat_sin_i[0] + BinBound_I[l])/2 - BinBound_I[0])/(
                    lat_sin_i[0] - BinBound_I[0]) + (
                    BinBound_I[l+1] - lat_sin_i[0])*(
                    lat_sin_i[1]-(BinBound_I[l+1] + lat_sin_i[0])/2)/(
                    lat_sin_i[1]-lat_sin_i[0]))*CosLat_I[0]
            Weight_II[l, 1] = (BinBound_I[l+1] - lat_sin_i[0])**2/(
                2*(lat_sin_i[1]-lat_sin_i[0]))*CosLat_I[1]
        elif (lat_sin_i[num_lat-1] < BinBound_I[l+1]):
            # LS_I[num_lat-2] <BB_I[l] < LS_U[num_lat-1] < BB_I[l+1]
            Weight_II[l, 0] = (lat_sin_i[num_lat-1] - BinBound_I[l])**2/(
                2*(lat_sin_i[num_lat-1]
                    - lat_sin_i[num_lat-2]))*CosLat_I[num_lat-2]
            Weight_II[l, 1] = ((BinBound_I[l+1] - lat_sin_i[num_lat-1])
                               * (BinBound_I[num_lat]
                                  - (lat_sin_i[num_lat-1]+BinBound_I[l+1])/2)
                               / (BinBound_I[num_lat]-lat_sin_i[num_lat-1])
                               + (lat_sin_i[num_lat-1]-BinBound_I[l])
                               * ((BinBound_I[l] + lat_sin_i[num_lat-1])/2
                                   - lat_sin_i[num_lat-2])
                               / (lat_sin_i[num_lat-1]-lat_sin_i[num_lat-2])
                               )*CosLat_I[num_lat-1]
        elif lMax_I[l] == lMin_I[l] + 1:
            # LS_I[lMin] <BB_I[l] < BB_I[l+1] < LS_I[lMax]
            Weight_II[l, 0] = CosLat_I[lMin_I[l]]*(
                BinBound_I[l+1] - BinBound_I[l])*(
                lat_sin_i[lMax_I[l]]-(BinBound_I[l+1] + BinBound_I[l])/2)/(
                    lat_sin_i[lMax_I[l]] - lat_sin_i[lMin_I[l]])
            Weight_II[l, 1] = CosLat_I[lMax_I[l]]*(
                BinBound_I[l+1] - BinBound_I[l])*(
                (BinBound_I[l+1] + BinBound_I[l])/2 - lat_sin_i[lMin_I[l]])/(
                lat_sin_i[lMax_I[l]] - lat_sin_i[lMin_I[l]])
        else:
            # LS_I[lMin] < BB_I[l] < LS_I[lMin+1
            # ..LS_I[lMax-1] < BB_I[l+1] < LS_I[lMax]
            Weight_II[l, 0] = CosLat_I[lMin_I[l]]*(
                lat_sin_i[lMin_I[l]+1] - BinBound_I[l])**2/(
                        2 * (lat_sin_i[lMin_I[l]+1] - lat_sin_i[lMin_I[l]]))
            Weight_II[l, 1] = CosLat_I[lMin_I[l]+1]*(
                lat_sin_i[lMin_I[l]+1] - BinBound_I[l])*(
                        (lat_sin_i[lMin_I[l]+1] + BinBound_I[l])/2
                        - lat_sin_i[lMin_I[l]]
                        )/(lat_sin_i[lMin_I[l]+1] - lat_sin_i[lMin_I[l]])
            Weight_II[l, lMax_I[l]-lMin_I[l]] = CosLat_I[lMax_I[l]]*(
                BinBound_I[l+1] - lat_sin_i[lMax_I[l]-1])**2/(
                        2*(lat_sin_i[lMax_I[l]] - lat_sin_i[lMax_I[l]-1]))
            Weight_II[l, lMax_I[l]-lMin_I[l]-1] = Weight_II[
                l, lMax_I[l]-lMin_I[l]-1] + CosLat_I[lMax_I[l]-1]*(
                BinBound_I[l+1] - lat_sin_i[lMax_I[l]-1])*(
                lat_sin_i[lMax_I[l]] - (
                    BinBound_I[l+1] + lat_sin_i[lMax_I[l]-1])/2)/(
                lat_sin_i[lMax_I[l]] - lat_sin_i[lMax_I[l]-1])
            if (lMax_I[l] - lMin_I[l] > 2):
                for l1 in np.arange(lMax_I[l] - lMin_I[l]-2):
                    Weight_II[l, 1+l1] = \
                        Weight_II[l, 1+l1] + CosLat_I[1+l1+lMin_I[l]]*(
                                lat_sin_i[lMin_I[l]+2+l1]
                                - lat_sin_i[lMin_I[l]+1+l1]
                                )/2
                    Weight_II[l, 2+l1] = \
                        Weight_II[l, 2+l1] + CosLat_I[2+l1+lMin_I[l]]*(
                                lat_sin_i[lMin_I[l]+2+l1]
                                - lat_sin_i[lMin_I[l]+1+l1])/2
        Weight_II[l, 0:lMax_I[l]-lMin_I[l]+1] = \
            Weight_II[l, 0:lMax_I[l]-lMin_I[l]+1]/(
                SinBinBound_I[l+1] - SinBinBound_I[l])

    br_uniform_c = np.zeros([num_lat, num_long])
    for i_long in np.arange(num_long):
        for i_lat in np.arange(num_lat):
            br_uniform_c[i_lat, i_long] = np.sum(
                Weight_II[i_lat, 0:lMax_I[i_lat]-lMin_I[i_lat]+1]
                * BrTransp_C[i_long, lMin_I[i_lat]:lMax_I[i_lat]+1])

    file_id = open('uniform.out', 'w')

    file_id.write('Uniform, non-smoothed magnetogram Br[Gauss]'+'\n')
    file_id.write('       0      0.00000       2       2       1 \n')
    file_id.write('      '+str(num_long)+'     '+str(num_lat)+'\n')
    file_id.write(str(long0) + '     '+str(long_earth)+' \n')
    file_id.write('Longitude Latitude Br long0 long_earth \n')

    for k in np.arange(num_lat):
        for l in np.arange(num_long):
            file_id.write("{0:6.1f} {1:6.1f} {2:14.6e}\n".format(
                (180./np.pi)*long_i[l], (180./np.pi)*lat_uniform_i[k],
                max([-b_max, min([b_max, br_uniform_c[k, l]])])))

    file_id.close()
    return (num_long, num_lat, num_param,
            param_i, long_i, lat_uniform_i,
            br_uniform_c)
