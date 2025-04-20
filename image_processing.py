from PIL import Image, ImageEnhance
import os

def process_image(path: str, flip: bool=False, contrast_min: float=-5.0, contrast_max: float=5.0) -> str:
    """
    - flip: horizontal flip if True
    - contrast_min/max: percent adjustments (e.g. -5.0 → 95%, +5.0 → 105%)
    """
    img = Image.open(path)

    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # calculate factor as midpoint of the two percents
    low  = 1.0 + (contrast_min / 100.0)
    high = 1.0 + (contrast_max / 100.0)
    factor = (low + high) / 2.0

    enhancer = ImageEnhance.Contrast(img)
    img2 = enhancer.enhance(factor)

    out_path = "processed_image.jpg"
    img2.save(out_path, "JPEG")
    return out_path
