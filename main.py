from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os, shutil, random
from PIL import Image, ImageEnhance

app = FastAPI()

# 1️⃣ Serve template + static + uploads
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Ensure folders exist
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# 2️⃣ Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 3️⃣ Upload & process
@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    saved = []
    out = []

    for f in files:
        # save original
        in_path = os.path.join("uploads", f.filename)
        with open(in_path, "wb") as buf:
            buf.write(await f.read())
        saved.append(in_path)

        # process
        proc = _process(in_path)
        out.append({
            "image":  proc.replace("\\", "/"),          # path for <img>
            "download_link": proc.replace("\\", "/")    # same path let user click to DL
        })

    return {"uploaded": saved, "processed": out}


def _process(path: str) -> str:
    img = Image.open(path)
    # subtle contrast bump
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)

    name = f"proc_{random.randrange(10000,99999)}.jpg"
    dst = os.path.join("uploads", name)
    img.save(dst)
    return dst
