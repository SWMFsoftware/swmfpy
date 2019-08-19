#!/usr/bin/env python3
"""
cleanomnidata.py

This script is to clean solar wind files to input into SWMF that has been retrieved from OMNIWeb.
"""
import sys
from omni2swmf import clean
from omni2swmf import read_data

USAGE_TEXT = "Usage:\n \
        ./cleanomnidata.py input.dat ouput.dat\n \
        input.dat:\n\t \
        Filename of input that has already been converted to SWMF solar wind file through omniweb2swmf.py.\n \
        output.dat:\n\t \
        Filename of output that will be cleaned."

def main():
    """
    Program run.
    """
    args = sys.argv
    try:
        data = read_data(args[1])
        ifile = open(args[1], 'r')
    except:
        print("Please specify input file.")
        print(USAGE_TEXT)
        sys.exit(1)
    try:
        ofile = open(args[2], 'w')
    except:
        print("Please specify output file.")
        print(USAGE_TEXT)
        sys.exit(1)
    b_x = clean(data['bx'])
    b_y = clean(data['by'])
    b_z = clean(data['bz'])
    v_x = clean(data['vx'])
    v_y = clean(data['vy'])
    v_z = clean(data['vz'])
    dens = clean(data['dens'])
    temp = clean(data['temp'])
    linenum = 0
    for line in ifile:
        if linenum < 3:
            ofile.write(line)
        else:
            ofile.write(line[:22] + ' ' +
                        str(b_x[linenum-3])[:5] + ' ' +
                        str(b_y[linenum-3])[:5] + ' ' +
                        str(b_z[linenum-3])[:5] + ' ' +
                        str(v_x[linenum-3])[:7] + ' ' +
                        str(v_y[linenum-3])[:7] + ' ' +
                        str(v_z[linenum-3])[:7] + ' ' +
                        str(dens[linenum-3])[:7] + ' ' +
                        str(temp[linenum-3])[:7] + '\n')
        linenum += 1

main()
