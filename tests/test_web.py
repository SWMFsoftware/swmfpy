#!/usr/bin/env python
"""Test for web.py
"""
from os.path import isfile
import datetime as dt
from swmfpy.web import *

TIME = dt.datetime(2016, 2, 3, 2, 1, 1)
TIMES = (dt.datetime(2016, 1, 2, 3), dt.datetime(2016, 3, 2, 1))

def test_download_magnetogram_adapt():
    download_magnetogram_adapt(TIME)
    assert isfile('adapt40311_03k012_201602030200_i00015600n1.fts')

def test_get_omni_data():
    data = get_omni_data(*TIMES)
    assert isinstance(data, dict), 'Incorrect type for omni data'
    assert data['times'][0] == TIMES[0], 'Starting time is incorrect'
