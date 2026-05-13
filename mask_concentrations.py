# -*- coding: utf-8 -*-
"""
Created on Mon May 11 16:07:29 2026

@author: rappe
"""
    
import os
from utils import applyMask, applyMaskRaster, exportImage

# output folder
output_path = r"assets/"
# create output folder if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

# initial concentration map
conc = "assets/init_conc_sp1.tif"
# output filename
filenam = "masked_conc_sp1.tif"
output_file = os.path.join(output_path, filenam)
# file to use as mask
mask_path = "assets/wall_domain.tif"

# mask conocentration
out_image, out_transform = applyMaskRaster(conc, mask_path)
# export image
exportImage(out_image, out_transform, output_file, conc)