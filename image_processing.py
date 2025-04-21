import os
import datetime
import piexif
from PIL import Image

def process_image(raw_path: str, processed_dir: str) -> str:
    # Load existing EXIF (or get empty dict if none)
    exif_dict = piexif.load(raw_path)
    # Update the DateTimeOriginal tag to now
    now_str = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = now_str.encode("utf-8")
    # Dump back to bytes
    exif_bytes = piexif.dump(exif_dict)

    # Build output path
    base, ext = os.path.splitext(os.path.basename(raw_path))
    out_name = f"{base}_processed{ext}"
    out_path = os.path.join(processed_dir, out_name)

    # Save with new EXIF
    img = Image.open(raw_path)
    img.save(out_path, exif=exif_bytes)

    return out_name
