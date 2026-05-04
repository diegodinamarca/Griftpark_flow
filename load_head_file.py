# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:16:02 2026

@author: rappe
"""

import rasterio
import numpy as np
def load_head_field(headfile):
    with rasterio.open(headfile) as src:
        data = src.read()
        transform = src.transform
        crs = src.crs
        nodata = src.nodata
    
    data = np.where(data == nodata, 0, data)
    # dimensiones en número de celdas
    nx = src.width   # columnas (x)
    ny = src.height  # filas (y)

    # tamaño de celda
    dx = transform.a
    dy = -transform.e  # suele ser negativo → lo hacemos positivo

    # longitud total
    Lx = nx * dx
    Ly = ny * dy
    return(data, Lx, Ly, nx, ny)
file = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/head_first_aquifer.tif"

head = load_head_field(file)