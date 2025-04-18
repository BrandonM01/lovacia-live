from PIL import Image, ImageEnhance

def process_image(image_path, flip=False, contrast_min=-5.0, contrast_max=5.0):
    # Open the image file
    img = Image.open(image_path)

    # Flip the image horizontally if needed
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Adjust contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast_min + (contrast_max - contrast_min) / 2)

    # Save the processed image
    img.save('processed_image.jpg')
    return 'processed_image.jpg'

