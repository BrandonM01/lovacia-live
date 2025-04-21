import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from image_processing import process_image

app = FastAPI()

# where to stash uploads + results
UPLOAD_DIR = "static/uploads"
PROCESSED_DIR = "static/processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# serve both folders under /static
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process-image")
async def upload_image(request: Request, file: UploadFile = File(...)):
    raw_path = os.path.join(UPLOAD_DIR, file.filename)
    # save uploaded bytes
    with open(raw_path, "wb") as f:
        f.write(await file.read())

    # run our EXIF‐update
    processed_filename = process_image(raw_path, PROCESSED_DIR)

    # show it back
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "original": f"/static/uploads/{file.filename}",
            "processed": f"/static/processed/{processed_filename}",
        },
    )
