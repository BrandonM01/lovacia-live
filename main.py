from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from PIL import Image, ImageEnhance
import random

app = FastAPI()

# Serve HTML templates
templates = Jinja2Templates(directory="templates")

# Ensure and mount static/ at /static
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure and mount uploads/ at /uploads
os.makedirs("uploads", exist_ok=True)    # <-- make sure this folder exists
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Handle image uploads
@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    upload_dir = "uploads"
    saved_files = []
    processed_files = []

    for file in files:
        # 1) Save original upload
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)

        # 2) Process and save new image into uploads/
        processed_image_path = process_image(file_path)

        # 3) Build URLs for preview & download
        filename = os.path.basename(processed_image_path)
        processed_files.append({
            "image": f"/uploads/{filename}",
            "download_link": f"/uploads/{filename}"
        })

    return {"uploaded": saved_files, "processed": processed_files}

# Image‑processing function
def process_image(file_path: str) -> str:
    try:
        img = Image.open(file_path)
        # Example effect: bump up contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        # Save back to uploads/
        processed_fn = f"processed_{random.randint(1000,9999)}.jpg"
        processed_path = os.path.join("uploads", processed_fn)
        img.save(processed_path)
        return processed_path

    except Exception as e:
        print(f"Error processing image: {e}")
        # If processing fails, just return original
        return file_path
