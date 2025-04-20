import os, random
from PIL import Image, ImageEnhance

def process_image_variants(path, base, ext, count, cmin, cmax, flip):
    out = []
    img0 = Image.open(path)
    for i in range(1, count+1):
        img = img0.copy()
        # contrast
        c = random.uniform(cmin, cmax)
        img = ImageEnhance.Contrast(img).enhance(1 + c/100)
        # flip
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        fname = f"{base}_img{i}{ext}"
        img.save(os.path.join("uploads", fname))
        out.append(fname)
    return out
