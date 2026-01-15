import os
from PIL import Image

# Absolute paths
src = r"d:\Codes\RNAfold_to_RNArtist\Dev_Tools\rna_icon.png"
dst = r"d:\Codes\RNAfold_to_RNArtist\RNAfold_App\rna_icon.ico"

if not os.path.exists(src):
    print(f"Error: Source image not found at {src}")
    exit(1)

img = Image.open(src)
print(f"Original image size: {img.size}")

# Force 256x256 with High Quality Resampling (LANCZOS)
# Windows will downscale this for smaller sizes, which often looks better than pre-generated small icons
img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)

# Save as single-size ICO to force Windows to use the high-res version
img_256.save(dst, format="ICO", sizes=[(256, 256)])
print(f"Icon created successfully at: {dst} (256x256 High Quality)")
