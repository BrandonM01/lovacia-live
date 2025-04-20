import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from video_processing import process_video_variants
from image_processing import process_image_variants

app = FastAPI()

# mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
PROCESSED_DIR = "static/processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def list_gallery():
    return sorted(os.listdir(PROCESSED_DIR))

@app.get("/")
async def index(request: Request):
    gallery = list_gallery()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "gallery": gallery,
    })

@app.post("/process-image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4().hex}{ext}"
    raw_path = os.path.join(UPLOAD_DIR, fname)
    with open(raw_path, "wb") as f:
        f.write(await file.read())

    # process and get list of output filenames
    out_files = process_image_variants(raw_path, PROCESSED_DIR)
    return RedirectResponse(url="/", status_code=303)

@app.post("/process-video")
async def upload_video(request: Request, file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4().hex}{ext}"
    raw_path = os.path.join(UPLOAD_DIR, fname)
    with open(raw_path, "wb") as f:
        f.write(await file.read())

    out_files = process_video_variants(raw_path, PROCESSED_DIR)
    return RedirectResponse(url="/", status_code=303)
