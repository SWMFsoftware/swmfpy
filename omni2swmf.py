#!/usr/bin/env python3
"""
Interpolate washed out data from OMNI
"""
from datetime import datetime as d
import numpy as np

def convert(infile, outfile):
    """
    Start the process of conversion.
    """
    # Write out the header
    outfile.write("OMNI file downloaded from https://omniweb.gsfc.nasa.gov/\n")
    outfile.write("yr mn dy hr min sec msec bx by bz vx vy vz dens temp\n")
    outfile.write("#START\n")
    # Begin conversion line by line
    for line in infile:
        date = d.strptime(line[:14], "%Y %j %H %M")
        correctline = date.strftime("%Y %m %d %H %M %S") + ' 000' + line[14:]
        outfile.write(correctline)
        #print(correctline)
    # Close files
    outfile.close()
    infile.close()

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
    return data

def read_data(filename):
    """
    Read the OMNI web data that was previously converted from omniweb2swmf.py
    filename:
        String of file name to input
    """
    data = np.genfromtxt(filename, dtype='float',
                         usecols=(7, 8, 9, 10, 11, 12, 13, 14),
                         names="bx,by,bz,vx,vy,vz,dens,temp",
                         skip_header=3)
    return data
