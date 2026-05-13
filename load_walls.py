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
        data = data[0, :, :]  # applyMask returns a list of arrays, we take the first one

    # Handle nodata values and flip y axis
    data = np.where(data == nodata, 0, data)
    data = data[::-1, :]

    return(data)

# filenam =  r"./assets/cement_walls.tif"
# x = load_cementwalls(filenam)
# print(x.shape)



    