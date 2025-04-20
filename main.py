import os
import traceback
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from image_processing import process_image
from video_processing import process_video_variants

# --- Configuration --------------------------------------------------------

UPLOAD_DIR    = "static/uploads"
PROCESSED_DIR = "static/processed"
THUMB_DIR     = "static/thumbs"
TEMPLATE_DIR  = "templates"

# --- App setup ------------------------------------------------------------

app = FastAPI()

# mount static folder so /static/... serves files
app.mount("/static", StaticFiles(directory="static"), name="static")

# set up Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# ensure our directories exist
for d in (UPLOAD_DIR, PROCESSED_DIR, THUMB_DIR):
    os.makedirs(d, exist_ok=True)

# --- Routes ---------------------------------------------------------------

@app.get("/")
async def index(request: Request):
    # list thumbnails in your thumb folder to show history/gallery
    thumbs = sorted(os.listdir(THUMB_DIR))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "thumbs": thumbs,
    })

@app.post("/process-image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    try:
        # save raw upload
        raw_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        # run your existing image pipeline
        out_files = process_image(raw_path)  
        # process_image() should return a list of output file paths or URLs

        return {"processed": out_files}

    except Exception as e:
        # print full Python traceback into the Render log
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/process-video")
async def upload_video(request: Request, file: UploadFile = File(...)):
    try:
        # save raw upload
        raw_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        # NOTE: process_video_variants now only takes 1 argument
        variants = process_video_variants(raw_path)
        # variants should be a dict or list describing your different video outputs

        return {"variants": variants}

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
