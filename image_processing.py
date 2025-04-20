import os
from PIL import Image

def process_image_variants(image_path: str) -> list[str]:
    """
    Open the image, generate a few thumbnails, save them under static/processed,
    and return the list of saved file paths.
    """
    img = Image.open(image_path)
    base, ext = os.path.splitext(os.path.basename(image_path))

    # define your variants here
    sizes = {
        "thumb": (150, 150),
        "medium": (400, 400),
        "large": (800, 800),
    }

    output_paths = []
    for suffix, (w, h) in sizes.items():
        variant = img.copy()
        variant.thumbnail((w, h))
        filename = f"{base}_{suffix}{ext}"
        out_path = os.path.join("static/processed", filename)
        variant.save(out_path)
        output_paths.append(out_path)

    return output_paths
