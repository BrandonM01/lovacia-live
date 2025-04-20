from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os
from image_processing import process_image_variants
from video_processing import process_video_variants

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    variants = process_image_variants(path)
    return {"original": path, "variants": variants}

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    variants = process_video_variants(path)
    return {"original": path, "variants": variants}

@app.get("/download/")
def download(file_path: str):
    return FileResponse(file_path, media_type="application/octet-stream", filename=os.path.basename(file_path))

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
import os, shutil

from image_processing import process_image_variants
from video_processing import process_video_variants

app = FastAPI()

#  ── serve your CSS/JS under /static
app.mount("/static", StaticFiles(directory="static"), name="static")

#  ── point Jinja at your templates dir
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home(request: Request):
    """
    Renders templates/index.html with a simple upload form.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    variants = process_image_variants(path)
    return {"original": path, "variants": variants}

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    variants = process_video_variants(path)
    return {"original": path, "variants": variants}

@app.get("/download/")
def download(file_path: str):
    return FileResponse(file_path, media_type="application/octet-stream", filename=os.path.basename(file_path))

