# -*- coding: utf-8 -*-
"""
Created on Mon May 11 11:29:05 2026

@author: rappe
"""

def load_wells(file, pumping_rate, layers=None):
    """
    Read a raster (.tif) with value 1 at well locations and return
    FloPy-style well stress period data.

    Parameters
    ----------
    file : str
        Path to raster file (.tif).
    pumping_rate : float
        Pumping rate assigned to each well.
    layers : list[int], optional
        Model layers where each well should be placed.
        Example: [0, 1, 2]

    Returns
    -------
    dict
        Dictionary in FloPy stress-period format:
        {0: [[lay, row, col, pumping_rate], ...]}
    """
    import rasterio
    import numpy as np

    if layers is None:
        layers = []

    with rasterio.open(file) as src:
        data = src.read(1)  # first raster band
        data = data[::-1, :]
        

    # Find raster cells where value == 1
    well_cells = np.argwhere(data == 1)

    # Build stress period data for stress period 0
    spd = []

    for row, col in well_cells:
        for lay in layers:
            spd.append([int(lay), int(row), int(col), pumping_rate])

    return spd

filenam = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/src/assets/wells.tif"
x = load_wells(filenam, 30, [3])
print(x)