#!/usr/bin/env python3
"""Interpolate washed out data from OMNI
"""
__author__ = "Qusai Al Shidi"

from datetime import datetime as d
import numpy as np
import pandas as pd


def combine_data(mfi_fname, swe_fname, plas_fname, coarse_filtering=False, **kwags):
    """Combines the csv files
    from cdaweb.sci.gsfc.nasa.gov into a pandas.DataFrame.

    Parameters:
        mfi_fname: AC_H0_MFI_***.csv
        swe_fname: AC_H0_SWE_***.csv
        plas_fname: WI_PM_3DP_***.csv
        coarse_filtering: Remove points where the value
                          is >3sigma from mean.
        returns: pandas.DataFrame object with solar wind data

    Make sure to download the csv files with
    the header seperated into a json file for safety.
    """
    # Read the csv files and set the index to dates
    with open(plas_fname, 'r') as pfile:
        ndata = pd.read_csv(pfile)
        ndata = ndata.set_index(pd.to_datetime(ndata[ndata.columns[0]]))
        ndata.index.names = ['date']
        ndata = ndata.drop(ndata.columns[0], 1)
        ndata = ndata.rename(columns={ndata.columns[0]: "density"})
    with open(mfi_fname, 'r') as bfile:
        bdata = pd.read_csv(bfile)
        bdata = bdata.set_index(pd.to_datetime(bdata[bdata.columns[0]]))
        bdata.index.names = ['date']
        bdata = bdata.drop(bdata.columns[0], 1)
        bdata = bdata.rename(columns={bdata.columns[0]: "bx",
                                      bdata.columns[1]: "by",
                                      bdata.columns[2]: "bz"})
    with open(swe_fname, 'r') as swfile:
        swdata = pd.read_csv(swfile)
        swdata = swdata.set_index(pd.to_datetime(swdata[swdata.columns[0]]))
        swdata.index.names = ['date']
        swdata = swdata.drop(swdata.columns[0], 1)
        swdata = swdata.rename(columns={swdata.columns[0]: "temperature",
                                        swdata.columns[1]: "vx",
                                        swdata.columns[2]: "vy",
                                        swdata.columns[3]: "vz"})
        # Clean erroneous data found in SWEPAM data from ACE
        for column in swdata.columns:
            swdata[column] = swdata[swdata[column].abs() < 1.e20][column]
    # Merge the data
    data = pd.merge(ndata, bdata, how='outer',
                    left_index=True, right_index=True)
    data = pd.merge(data, swdata, how='outer',
                    left_index=True, right_index=True)
    # Interpolate and fill
    data = data.interpolate().ffill().bfill()
    # Coarse filtering
    if coarse_filtering:
        for column in data.columns:
            mean = data[column].mean()
            sigma = data[column].std()
            data[column] = data[data[column].abs() < mean+3*sigma][column]
        data = data.interpolate().ffill().bfill()
    return data


def write_data(data, outfilename="IMF.dat", enable_rb=True):
    """Writes the pandas.DataFrame into an input file
    that SWMF can read as input IMF (IMF.dat).

    Parameters:
        data: pandas.DataFrame object with solar wind data
        outfilename: The output file name for ballistic solar wind data. \
                (default: "IMF.dat")
        enable_rb: Enables solar wind input for the radiation belt model. \
                (default: True)
    """
    # Generate BATS-R-US solar wind input file
    with open(outfilename, 'w') as outfile:
        outfile.write("CSV files downloaded from\
                       https://cdaweb.gsfc.nasa.gov/\n")
        outfile.write("yr mn dy hr min sec msec \
                       bx by bz vx vy vz dens temp\n")
        outfile.write("#START\n")
        for index, rows in data.iterrows():
            outfile.write(index.strftime("%Y %m %d %H %M %S") + ' ')
            outfile.write(index.strftime("%f")[:3] + ' ')
            outfile.write(str(rows['bx']) + ' ')
            outfile.write(str(rows['by']) + ' ')
            outfile.write(str(rows['bz']) + ' ')
            outfile.write(str(rows['vx']) + ' ')
            outfile.write(str(rows['vy']) + ' ')
            outfile.write(str(rows['vz']) + ' ')
            outfile.write(str(rows['density']) + ' ')
            outfile.write(str(rows['temperature']) + ' ')
            outfile.write('\n')
        # Generate RBE model solar wind input file
        if enable_rb:
            with open("RB.SWIMF", 'w') as rbfile:
                # Choose first element as t=0 header (unsure if this is safe)
                rbfile.write(data.index[0].strftime("%Y, %j, %H ")
                             + "! iyear, iday, ihour corresponding to t=0\n")
                # TODO: add option to change swlag time
                rbfile.write("2640.  "
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
                                 + str(rows['density'])[:8]
                                 + "     "
                                 # Speed magnitude
                                 + str(np.sqrt(rows['vx']**2
                                       + rows['vz']**2
                                       + rows['vy']**2))[:8]
                                 + '\n')

    def convert(infile, outfile="IMF.dat"):
        """Start the process of conversion of OMNI file to
        SWMF IMF input file.
        """
        # Write out the header
        outfile.write("OMNI file downloaded from \
                       https://omniweb.gsfc.nasa.gov/\n")
        outfile.write("yr mn dy hr min sec msec bx by bz vx vy vz dens temp\n")
        outfile.write("#START\n")
        # Begin conversion line by line
        for line in infile:
            date = d.strptime(line[:14], "%Y %j %H %M")
            correctline = date.strftime("%Y %m %d %H %M %S")\
                + ' 000' + line[14:]
            outfile.write(correctline)
        # Close files
        outfile.close()
        infile.close()


# REWRITE IN PANDAS
def clean(data):
    """
    Cleans the data for bad discontinuities.
    data:
        numpy array of data
    return:
        numpy array of cleaned data
    """
    prevdata = data[0]
    nextdata = data[1]
    prevlocation = 0
    nextlocation = 1
    baddata = False
    for loc in range(1, np.size(data)):
        if (data[loc] == 9999.99 or data[loc] == 99999.9 or data[loc] == 9999999. or data[loc] == 999.99) and baddata is False:
            prevlocation = loc-1
            prevdata = data[loc-1]
            baddata = True
        elif (data[loc] != 9999.99 and data[loc] != 99999.9 and data[loc] != 9999999. and data[loc] != 999.99) and baddata is True:
            nextlocation = loc
            nextdata = data[loc]
            baddata = False
            length = nextlocation-prevlocation
            replacedata = np.linspace(prevdata, nextdata, length+1)
            data[prevlocation:nextlocation+1] = replacedata
        if loc == np.size(data)-1 and baddata is True:
            nextlocation = loc
            nextdata = prevdata
            baddata = False
            length = nextlocation-prevlocation
            replacedata = np.linspace(prevdata, nextdata, length+1)
            data[prevlocation:nextlocation+1] = replacedata
    return data


def read_data(filename):
    """
    Read the OMNI web data that was previously converted from omniweb2swmf.py
    filename:
        String of file name to input
    return:
        numpy array of data
    """
    data = np.genfromtxt(filename, dtype='float',
                         usecols=(7, 8, 9, 10, 11, 12, 13, 14),
                         names="bx,by,bz,vx,vy,vz,dens,temp",
                         skip_header=3)
    return data
