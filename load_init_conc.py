# -*- coding: utf-8 -*-
"""
Created on Mon May 11 13:14:00 2026

@author: rappe
"""
import rasterio
import numpy as np
def load_init_conc(filenam):
    with rasterio.open(filenam) as src:
        # Get the window for the common bounds
        # window = src.window(left, bottom, right, top)
        data = src.read(1)
        nodata = src.nodata
        
        # Handle nodata values and flip y axis
        data = np.where(data == nodata, 0, data)
        data = data[::-1, :]
        return(data)