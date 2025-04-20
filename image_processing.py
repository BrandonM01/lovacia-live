import os
import piexif
from PIL import Image

def modify_exif(input_path: str, out_dir: str) -> str:
    """
    Reads the JPEG at input_path, injects a "UserComment"
    EXIF tag with a timestamp, and writes it to out_dir.
    Returns the full path to the new file.
    """
    # Load image & existing EXIF
    img = Image.open(input_path)
    exif_dict = piexif.load(img.info.get("exif", b""))

    # Add/update a UserComment
    from datetime import datetime
    comment = f"Processed on {datetime.utcnow().isoformat()}Z"
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
        comment, encoding="unicode"
    )

    # Build output filename
    filename = os.path.basename(input_path)
    out_path = os.path.join(out_dir, f"meta_{filename}")

    # Export with new EXIF
    exif_bytes = piexif.dump(exif_dict)
    img.save(out_path, "jpeg", exif=exif_bytes)
    return out_path
