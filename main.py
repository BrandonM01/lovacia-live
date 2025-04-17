from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageEnhance
import os, random

app = FastAPI()

# ensure our dirs exist
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# mount those dirs so FastAPI can serve the images
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# set up Jinja2
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    processed = []

    for upload in files:
        # 1) save original
        orig_path = os.path.join("uploads", upload.filename)
        with open(orig_path, "wb") as f:
            f.write(await upload.read())

        # 2) open + apply a random subtle contrast tweak
        img = Image.open(orig_path)
        factor = random.uniform(0.9, 1.1)  # subtle: ±10%
        img = ImageEnhance.Contrast(img).enhance(factor)

        # 3) save processed copy under static/
        base, ext = os.path.splitext(upload.filename)
        out_name = f"{base}_{random.randint(1000,9999)}.jpg"
        out_path = os.path.join("static", out_name)
        img.save(out_path, "JPEG")

        processed.append({
            "image": f"/static/{out_name}",
            "download_link": f"/static/{out_name}"
        })

    return {"processed": processed}
