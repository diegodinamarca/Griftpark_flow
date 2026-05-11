# -*- coding: utf-8 -*-
"""
Created on Mon May 11 16:07:29 2026

@author: rappe
"""
    
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import os

def maskConcentrations(conc, mask_path):
    with rasterio.open(conc) as src:
        gdf = gpd.read_file(mask_path)
        
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)

        shapes = [geom.__geo_interface__ for geom in gdf.geometry]

        out_image, out_transform = mask(src, shapes, crop=False)

    return out_image, out_transform

def export_image(conc, output_path, output_file):
    src = rasterio.open(conc)
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(out_image)

# output folder
output_path = r"C:\Users\rappe\OneDrive\Documentos\Master Courses\EnvH\Griftpark"
# initial concentration map
conc = "assets/init_conc_sp3.tif"
# output filename
filenam = "masked_conc_sp3.tif"
output_file = os.path.join(output_path, filenam)
# file to use as mask
mask_path = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/domain_1.shp"

# mask conocentration
out_image, out_transform = maskConcentrations(conc, mask_path)
# export image
export_image(conc, output_path, output_file)