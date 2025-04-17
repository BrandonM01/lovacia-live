from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageEnhance
import os, random

app = FastAPI()

# ensure directories
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_images(
    batch_size:    int     = Form(5),
    contrast_min:  float   = Form(-5.0),
    contrast_max:  float   = Form(5.0),
    flip:          bool    = Form(False),
    files:         list[UploadFile] = File(...)
):
    processed = []

    for upload in files[:batch_size]:
        orig_path = os.path.join("uploads", upload.filename)
        with open(orig_path, "wb") as f:
            f.write(await upload.read())

        img = Image.open(orig_path)
        factor = random.uniform(contrast_min, contrast_max) / 100 + 1
        img = ImageEnhance.Contrast(img).enhance(factor)
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

        base, _ = os.path.splitext(upload.filename)
        out_name = f"{base}_{random.randint(1000,9999)}.jpg"
        out_path = os.path.join("static", out_name)
        img.save(out_path, "JPEG")

        processed.append({
            "image": f"/static/{out_name}",
            "download_link": f"/static/{out_name}"
        })

    return {"processed": processed}
