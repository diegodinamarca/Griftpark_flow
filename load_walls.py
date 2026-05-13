# -*- coding: utf-8 -*-
"""
Created on Mon May  4 19:27:25 2026

@author: rappe
"""
import rasterio
import numpy as np
from utils import applyMask

def load_cementwalls(file, mask=None):
    with rasterio.open(file) as src:
        # Get the window for the common bounds
        # window = src.window(left, bottom, right, top)
        data = src.read(1)
        nodata = src.nodata

    if mask is not None:
        data, transform = applyMask(file, mask, crop=True)
        print(f"data.shape after masking: {data.shape}")
        data = data[0, :, :]  # applyMask returns a list of arrays, we take the first one
        print(f"Cement walls data shape after masking: {data.shape}")

    # Handle nodata values and flip y axis
    data = np.where(data == nodata, 0, data)
    data = data[::-1, :]
    print(f"Cement walls data shape after nodata handling and flipping: {data.shape}")

    return(data)

# filenam =  r"./assets/cement_walls.tif"
# x = load_cementwalls(filenam)
# print(x.shape)



    