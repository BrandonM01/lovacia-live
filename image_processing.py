from PIL import Image, ImageEnhance
import os

def process_image(input_path: str, flip: bool, contrast_min: float, contrast_max: float, count: int) -> str:
    img = Image.open(input_path)
    # optionally flip
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    # adjust contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1 + (contrast_min / 100.0))
    img = enhancer.enhance(1 + (contrast_max / 100.0))
    # save output
    out_path = input_path.replace(".", f"_proc.")
    img.save(out_path, format="JPEG")
    return out_path
