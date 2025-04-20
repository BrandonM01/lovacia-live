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
