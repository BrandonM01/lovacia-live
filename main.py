from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from moviepy.editor import VideoFileClip
from PIL import Image, ImageEnhance
import os
import shutil
import random
import string
from pathlib import Path
from io import BytesIO
import tempfile

app = FastAPI()

# Serving static files (e.g., uploaded images or videos)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define the working directory for uploads
UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def generate_random_string(length=10):
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the index.html page."""
    with open("templates/index.html") as f:
        return f.read()


@app.post("/upload/")
async def upload_files(
    files: list[UploadFile] = File(...),
    batch_size: int = 5,
    contrast_min: float = -5.0,
    contrast_max: float = 5.0,
    flip: bool = False
):
    """Handle file upload and process videos/images."""
    # Create a temp directory to store uploaded files
    temp_dir = tempfile.mkdtemp()

    file_paths = []
    for file in files:
        # Save each uploaded file to the temporary directory
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(file_location)

    # Process each file (flip, adjust contrast)
    processed_files = []
    for file_path in file_paths:
        if file_path.lower().endswith(('.mp4', '.avi', '.mov')):  # Check for video
            # Process video (e.g., adjust contrast and flip)
            clip = VideoFileClip(file_path)
            clip = clip.fl_image(lambda image: adjust_contrast(image, contrast_min, contrast_max))
            if flip:
                clip = clip.fx(vfx.mirror_x)
            output_path = os.path.join(temp_dir, generate_random_string() + ".mp4")
            clip.write_videofile(output_path)
            processed_files.append(output_path)
            clip.close()
        else:  # Process image
            img = Image.open(file_path)
            img = adjust_contrast(img, contrast_min, contrast_max)
            if flip:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            output_path = os.path.join(temp_dir, generate_random_string() + ".jpg")
            img.save(output_path)
            processed_files.append(output_path)

    # Clean up temporary files (optional)
    shutil.rmtree(temp_dir)

    return {"processed_files": processed_files}


def adjust_contrast(image, min_value: float, max_value: float):
    """Adjust the contrast of an image."""
    enhancer = ImageEnhance.Contrast(image)
    factor = random.uniform(min_value, max_value)
    return enhancer.enhance(factor)


@app.get("/gallery/")
async def get_gallery():
    """Fetch processed video/image history."""
    return {"history": os.listdir(UPLOAD_DIR)}

