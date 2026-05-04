# -*- coding: utf-8 -*-
"""
Created on Mon May  4 19:27:25 2026

@author: rappe
"""
import rasterio
import numpy as np
def load_cementwalls(file, left, bottom, right, top):
    with rasterio.open(file) as src:
        # Get the window for the common bounds
        window = src.window(left, bottom, right, top)
        data = src.read(1, window=window)
        nodata = src.nodata
        
        # Handle nodata values and flip y axis
        data = np.where(data == nodata, 0, data)
        data = data[::-1, :]
        return(data)
    

        
    