# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:16:02 2026

@author: rappe
"""

import rasterio
import numpy as np
from utils import applyMask

def load_head_field(headfile, mask=None):
    with rasterio.open(headfile) as src:
        data = src.read(1)
        transform = src.transform
        nodata = src.nodata
        ncol = data.shape[1]   # columnas (x)
        nrow = data.shape[0]
        # print(f"Original head data shape: {data.shape}, nodata value: {nodata}")

    if mask is not None:
        data, transform = applyMask(headfile, mask, crop=True)
        if data.ndim == 3 and data.shape[0] == 1:
            data = data[0]
        # dimensiones en número de celdas
        ncol = data.shape[1]   # columnas (x)
        nrow = data.shape[0]   # filas (y)
        # print(f"Head data shape after masking: {data.shape}")
    
    data = np.where(data == nodata, 0, data)
    data = data[::-1, :]

    # print(("data sample", data[0:5, 0:5]))
    # tamaño de celda
    delc = transform.a
    delr = -transform.e  # suele ser negativo → lo hacemos positivo

    # longitud total
    Lx = ncol * delr
    Ly = nrow * delc
    return(data, delc, delr, ncol, nrow, Lx, Ly)


def get_common_extent(headfiles):
    """
    Reads a list of headfiles (GeoTIFF rasters) and returns the grid parameters
    for the common extent among all rasters.
    
    Parameters:
    headfiles (list): List of file paths to the headfile rasters.
    
    Returns:
    tuple: (delc, delr, ncol, nrow, Lx, Ly) for the common extent.
    """
    if not headfiles:
        raise ValueError("No headfiles provided")
    
    bounds_list = []
    transforms = []
    
    for hf in headfiles:
        with rasterio.open(hf) as src:
            bounds_list.append(src.bounds)
            transforms.append(src.transform)
    
    # Assume all rasters have the same cell sizes
    delc = transforms[0].a
    delr = -transforms[0].e
    
    # Verify all have the same cell sizes
    for t in transforms[1:]:
        print(f"Checking cell sizes: delc={delc}, delr={delr} against {t.a}, {-t.e}")
        if abs(t.a - delc) > 1e-1 or abs(-t.e - delr) > 1e-1:
            raise ValueError("Rasters have different cell sizes")
    
    # Find the intersection bounds
    left = max(b.left for b in bounds_list)
    bottom = max(b.bottom for b in bounds_list)
    right = min(b.right for b in bounds_list)
    top = min(b.top for b in bounds_list)
    
    if left >= right or bottom >= top:
        raise ValueError("No common extent among the rasters")
    
    # Calculate the dimensions of the common extent
    Lx = right - left
    Ly = top - bottom
    
    # Number of cells (using floor division to get full cells)
    ncol = int(Lx // delr)
    nrow = int(Ly // delc)
    
    # Adjust Lx and Ly to match the grid
    Lx = ncol * delr
    Ly = nrow * delc
    
    # Adjust bounds to match the grid
    right = left + Lx
    top = bottom + Ly
    
    return delc, delr, ncol, nrow, Lx, Ly, left, bottom, right, top


def get_clipped_head_data(headfiles):
    """
    Reads a list of headfiles (GeoTIFF rasters), clips them to the common extent,
    and returns the clipped data arrays along with the common grid parameters.
    
    Parameters:
    headfiles (list): List of file paths to the headfile rasters.
    
    Returns:
    tuple: (clipped_data_list, delc, delr, ncol, nrow, Lx, Ly)
           where clipped_data_list is a list of numpy arrays (one per headfile),
           each with shape (nrow, ncol).
    """
    delc, delr, ncol, nrow, Lx, Ly, left, bottom, right, top = get_common_extent(headfiles)
    
    clipped_data_list = []
    
    for hf in headfiles:
        with rasterio.open(hf) as src:
            # Get the window for the common bounds
            window = src.window(left, bottom, right, top)
            data = src.read(1, window=window)
            nodata = src.nodata
            
            # Handle nodata values and flip y axis
            data = np.where(data == nodata, 0, data)
            data = data[::-1, :]
            
            # Ensure the shape matches (nrow, ncol)
            if data.shape != (nrow, ncol):
                raise ValueError(f"Clipped data shape {data.shape} does not match expected ({nrow}, {ncol}) for {hf}")
            
            clipped_data_list.append(data)
    
    return clipped_data_list
