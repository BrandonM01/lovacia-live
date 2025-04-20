from PIL import Image, ImageOps
import os
from typing import List

def process_image_variants(input_path: str) -> List[str]:
    """
    Given an input image, produce two variants:
      1) grayscale
      2) mirrored
    Returns list of output file paths.
    """
    img = Image.open(input_path)
    base, ext = os.path.splitext(input_path)

    # 1) grayscale
    gray_path = f"{base}_gray{ext}"
    img.convert("L").save(gray_path)
    
    # 2) mirrored
    mirror_path = f"{base}_mirror{ext}"
    ImageOps.mirror(img).save(mirror_path)

    return [gray_path, mirror_path]
