import os
from utils import applyMask, exportImage

# output folder
output_path = r"C:\Users\rappe\OneDrive\Documentos\Master Courses\EnvH\Griftpark\src\assets\masked"
# create output folder if it doesn't exist
if not os.path.exists(output_path):
    os.makedirs(output_path)

# file to use as mask
mask_path = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/study_area_extent_250m.geojson"

# get a list of all the file in a folder
folder = r"C:\Users\rappe\OneDrive\Documentos\Master Courses\EnvH\Griftpark\src\assets"
files = os.listdir(folder)
print(files)

# apply mask to all the files in the folder
for file in files:
    if file.endswith(".tif"):
        f = os.path.join(folder, file)
        print(f"Processing file: {file}")
        out_image, out_transform = applyMask(f, mask_path, crop=True)
        output_file = os.path.join(output_path, file)
        print(f"Exporting masked image to: {output_file}")
        exportImage(out_image, out_transform, output_file, f)
