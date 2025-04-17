from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from PIL import Image, ImageEnhance
import random
from fastapi import Request

app = FastAPI()

# Serve HTML templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve static files (for CSS/logo if needed)
os.makedirs("static", exist_ok=True)

# Route: Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route: Handle image uploads
@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    saved_files = []
    processed_files = []

    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        saved_files.append(file_path)

        # Process the image
        processed_image_path = process_image(file_path)
        processed_files.append({
            "image": f"/uploads/{os.path.basename(processed_image_path)}",
            "download_link": f"/uploads/{os.path.basename(processed_image_path)}"
        })

    return {"uploaded": saved_files, "processed": processed_files}

# Process Image Function
def process_image(file_path: str) -> str:
    try:
        # Open the image
        img = Image.open(file_path)

        # Enhance the image (example: convert to black and white)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        # Generate a random name for the processed image
        processed_file_name = f"processed_{random.randint(1000, 9999)}.jpg"
        processed_path = os.path.join("static", processed_file_name)

        # Save the processed image
        img.save(processed_path)
        return processed_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return file_path
