# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 18:03:14 2026

@author: rappe
"""
import os
import flopy
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask

def timeIndexForMaxConc(model_ws, obs_row, obs_col):
    # ===== READ CONCENTRATION FILE =====
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    # Get available times
    times_mt = ucnobj.get_times()
    # Get concentration at observation point for all times
    conc = ucnobj.get_alldata()
    conc_obs = conc[:, 0, obs_row, obs_col]
    ind = np.argmax(conc_obs)
    return(ind)

def getConcMatrix(model_ws, timestp):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    times_mt = ucnobj.get_times()
    conc = ucnobj.get_data(totim=times_mt[timestp])
    return conc


def getTimes(model_ws):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    # Get available times
    times_mt = ucnobj.get_times()
    return(times_mt)

def getPointConc(model_ws, obs_row, obs_col):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    
    # Get available times
    times_mt = ucnobj.get_times()
    
    print(f"Number of output times: {len(times_mt)}")
    print(f"Time range: {times_mt[0]:.1f} to {times_mt[-1]:.1f} days")
    
    # Get concentration at observation point for all times
    conc = ucnobj.get_alldata()
    conc_obs = conc[:, 0, obs_row, obs_col]
    return(conc_obs)

def applyMask(filenam, mask_path, crop=True):
    with rasterio.open(filenam) as src:
        gdf = gpd.read_file(mask_path)
        print(f"source no data value: {src.nodata}")
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)

        shapes = [geom.__geo_interface__ for geom in gdf.geometry]

        out_image, out_transform = mask(src, shapes, crop=crop, nodata=src.nodata, filled=True)

    return out_image, out_transform

def applyMaskRaster(filenam, mask_raster_path):
    """
    Apply a raster-based mask to an image.
    
    Parameters:
    -----------
    filenam : str
        Path to the source raster file to be masked
    mask_raster_path : str
        Path to the raster mask file (pixels == 1 are kept, all others are masked out)
    
    Returns:
    --------
    out_image : np.ndarray or np.ma.MaskedArray
        Masked image data
    out_transform : rasterio.transform.Affine
        Geospatial transform of the output image
    """
    with rasterio.open(filenam) as src:
        with rasterio.open(mask_raster_path) as mask_src:

            # Check if CRS match
            if mask_src.crs != src.crs:
                print(f"Warning: CRS mismatch. Source: {src.crs}, Mask: {mask_src.crs}")
            
            # Read the mask raster with masked array handling for nodata
            mask_data = mask_src.read(1, masked=True)
            
            # Get the nodata value from the mask
            mask_nodata = mask_src.nodata
            
            # Create a boolean mask: True where we want to KEEP data (mask == 1)
            # Everything else (mask != 1) will be masked out
            if isinstance(mask_data, np.ma.MaskedArray):
                # Create mask for areas where mask_data == 1 and is not masked
                keep_pixels = (mask_data == 1) & ~mask_data.mask
            else:
                # If not masked, just check where mask_data == 1
                keep_pixels = mask_data == 1
            
            print(f"Mask stats - Total pixels: {mask_data.size}, Pixels to keep: {np.sum(keep_pixels)}")
            
            # Read source data and apply mask
            src_data = src.read()
            
            # Apply the mask to all bands
            nodata_val = src.nodata if src.nodata is not None else src_data.dtype.type(0)
  
            # Create masked array - mask is True where we want to HIDE data
            out_image = np.ma.masked_array(
                src_data,
                mask=np.broadcast_to(~keep_pixels, src_data.shape),
                fill_value=nodata_val
            )
            
            out_transform = src.transform

    return out_image, out_transform

def exportImage(out_image, out_transform, output_file, src_file):
    src = rasterio.open(src_file)
    out_meta = src.meta.copy()
    
    # Determine nodata value based on dtype and source file
    if src.nodata is not None:
        nodata_val = src.nodata
    else:
        # Use appropriate nodata value for the dtype
        dtype = out_image.dtype
        if dtype == np.uint8:
            nodata_val = 0
        elif dtype in [np.int16, np.int32, np.int64]:
            nodata_val = -9999
        elif dtype in [np.float32, np.float64]:
            nodata_val = -9999.0
        else:
            nodata_val = 0
    
    # If it's a masked array, fill masked values with nodata
    if isinstance(out_image, np.ma.MaskedArray):
        out_image = out_image.filled(nodata_val)

    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        "nodata": nodata_val
    })
    print(f"Exporting masked image to {output_file}")
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(out_image)