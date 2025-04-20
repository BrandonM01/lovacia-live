import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from image_processing import process_image_variants
from video_processing import process_video_variants

# where we save uploads & outputs
UPLOAD_DIR = "static/uploads"
PROCESSED_DIR = "static/processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

app = FastAPI()

# serve /static/**
app.mount("/static", StaticFiles(directory="static"), name="static")

# templates lives under templates/
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    """
    Home page: renders your upload form.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process-image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    """
    1. Save the incoming image to UPLOAD_DIR
    2. Run through all your PIL variants
    3. Render a gallery template with the new URLs
    """
    # save raw upload
    raw_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(raw_path, "wb") as out:
        out.write(await file.read())

    # process & get back list of filepaths under static/processed
    out_paths = process_image_variants(raw_path)

    # convert to URLs for the template
    urls = [f"/static/processed/{os.path.basename(p)}" for p in out_paths]

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "images": urls,
        },
    )


@app.post("/process-video")
async def upload_video(file: UploadFile = File(...)):
    """
    1. Save the incoming video to UPLOAD_DIR
    2. Run through your moviepy variants
    3. Return the first processed file directly
    """
    raw_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(raw_path, "wb") as out:
        out.write(await file.read())

    out_paths = process_video_variants(raw_path, PROCESSED_DIR)

    # serve the first variant back
    first = out_paths[0]
    return FileResponse(
        first,
        media_type="video/mp4",
        filename=os.path.basename(first),
    )
