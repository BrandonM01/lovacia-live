from PIL import Image, ImageEnhance
import os

def process_image(path, flip, contrast_min, contrast_max, suffix=""):
    img = Image.open(path)
    # apply contrast & flip...
    out_name = os.path.splitext(os.path.basename(path))[0] + suffix + ".jpg"
    out_path = os.path.join("uploads", out_name)
    img.save(out_path)
    return out_name
