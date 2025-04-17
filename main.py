from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from PIL import Image, ImageEnhance
import random

app = FastAPI()

# Serve HTML templates
templates = Jinja2Templates(directory="templates")

# Serve files in the static/ folder at /static/...
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── ADD THIS LINE ───
# Serve files in the uploads/ folder at /uploads/...
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# ──────────────────────

# Route: Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route: Handle image uploads
@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    upload_dir = "uploads"
    # (folder already created above)
    saved_files = []
    processed_files = []

    for file in files:
        # 1) Save the raw upload
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file_path)

        # 2) Process it
        processed_image_path = process_image(file_path)

        # 3) Add URLs for preview + download
        processed_files.append({
            "image": f"/uploads/{os.path.basename(processed_image_path)}",
            "download_link": f"/uploads/{os.path.basename(processed_image_path)}"
        })

    return {"uploaded": saved_files, "processed": processed_files}

# Process Image Function
def process_image(file_path: str) -> str:
    try:
        img = Image.open(file_path)

        # (Example processing—tweak as you like)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        # Save the result back into uploads/ (so the browser can fetch it)
        processed_fn = f"processed_{random.randint(1000,9999)}.jpg"
        processed_path = os.path.join("uploads", processed_fn)

        img.save(processed_path)
        return processed_path

    except Exception as e:
        print(f"Error processing image: {e}")
        # Fallback: return original so at least something shows
        return file_path
