#!/usr/bin/env python3
"""
Plot the cleaned omni data
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from omni2swmf import read_data
from omni2swmf import clean

START_DATE = 14
END_DATE = 18
def plotv():
    """ Plot magnetic fields """
    args = sys.argv
    try:
        data = read_data(args[1])
    except:
        print("Please provide the cleaned omni file as input.")
    plt.subplot(3, 1, 1)
    x_axis = np.linspace(START_DATE, END_DATE, np.size(data['bx']))
    plt.plot(x_axis, clean(data['vx']))
    plt.ylabel('$V_x$ [km s$^{-1}$]')
    plt.subplot(3, 1, 2)
    plt.plot(x_axis, clean(data['vy']))
    plt.ylabel('$V_y$ [km s$^{-1}$]')
    plt.subplot(3, 1, 3)
    plt.plot(x_axis, clean(data['vz']))
    plt.ylabel('$V_z$ [km s$^{-1}$]')
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

def plotb():
    """ Plot magnetic fields """
    args = sys.argv
    try:
        data = read_data(args[1])
    except:
        print("Please provide the cleaned omni file as input.")
    plt.subplot(3, 1, 1)
    x_axis = np.linspace(START_DATE, END_DATE, np.size(data['bx']))
    plt.plot(x_axis, clean(data['bx']))
    plt.ylabel('$B_x$ [nT]')
    plt.subplot(3, 1, 2)
    plt.plot(x_axis, clean(data['by']))
    plt.ylabel('$B_y$ [nT]')
    plt.subplot(3, 1, 3)
    plt.plot(x_axis, clean(data['bz']))
    plt.ylabel('$B_z$ [nT]')
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

def plotnt():
    """ Plot magnetic fields """
    args = sys.argv
    try:
        data = read_data(args[1])
    except:
        print("Please provide the cleaned omni file as input.")
    plt.subplot(2, 1, 1)
    x_axis = np.linspace(START_DATE, END_DATE, np.size(data['bx']))
    plt.plot(x_axis, clean(data['dens']))
    plt.ylabel('Density [$1/cm^{-3}$]')
    plt.subplot(2, 1, 2)
    plt.plot(x_axis, clean(data['temp']))
    plt.ylabel('$T$ [K]')
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

plotv()
