from PIL import Image, ImageEnhance

def process_image(input_image_path, flip=False, contrast_min=-5.0, contrast_max=5.0):
    # Open the image
    img = Image.open(input_image_path)
    
    # Apply contrast adjustment
    contrast = ImageEnhance.Contrast(img).enhance(1 + contrast_min / 100)  # Adjust this based on contrast_min/max

    # Optionally flip the image
    if flip:
        contrast = contrast.transpose(Image.FLIP_LEFT_RIGHT)

    # Save the processed image
    output_image_path = "processed_" + input_image_path
    contrast.save(output_image_path)

    return output_image_path  # Return the processed image path
