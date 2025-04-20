from PIL import Image, ImageEnhance

def process_image(
    path: str,
    flip: bool = False,
    contrast_min: float = -20.0,
    contrast_max: float = 20.0
) -> str:
    # open & optionally flip
    img = Image.open(path)
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # adjust contrast
    enhancer = ImageEnhance.Contrast(img)
    # map contrast_min..contrast_max (percent) to a factor around 1.0
    factor = 1 + ((contrast_max - contrast_min) / 100.0)
    img = enhancer.enhance(factor)

    # save output
    output = "processed_image.jpg"
    img.save(output, "JPEG")
    return output
