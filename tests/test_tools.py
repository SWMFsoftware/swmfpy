#!/usr/bin/env python
"""Tests for tools.py
"""
import numpy as np
from swmfpy.tools import *

def test_interp_nans():
    y__ = np.array([1, 1, np.NaN, 1])
    x__ = np.ones_like(y__)
    assert not any(np.isnan(interp_nans(x__, y__)))
