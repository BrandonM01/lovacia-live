from PIL import Image, ImageEnhance

def process_image(
    input_path: str,
    flip: bool = False,
    contrast_min: float = 0.8,
    contrast_max: float = 1.2,
) -> str:
    im = Image.open(input_path)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    enhancer = ImageEnhance.Contrast(im)
    factor = (contrast_min + contrast_max) / 2
    im = enhancer.enhance(factor)
    output_path = "processed_image.jpg"
    im.save(output_path, format="JPEG")
    return output_path
