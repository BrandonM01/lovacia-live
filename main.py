import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from image_processing import modify_exif

# Directories
UPLOAD_DIR = "static/uploads"
PROCESSED_DIR = "static/processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# App & templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        # 1) Save incoming file
        raw_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        # 2) Modify its EXIF and save
        out_path = modify_exif(raw_path, PROCESSED_DIR)

        # 3) Return JSON with the new URL
        url = out_path.replace("static/", "/static/")
        return JSONResponse({"processed_image_url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
