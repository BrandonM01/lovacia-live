from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, zipfile, random
from PIL import Image, ImageEnhance

app = FastAPI()

templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_images(
    files: list[UploadFile] = File(...),
    count:   int   = Form(1),
    contrast: float = Form(1.02),    # subtle default bump
    rotation: int   = Form(2),       # subtle default rotate
    crop:     float = Form(0.02)     # subtle default crop‐percent
):
    upload_dir = "uploads"
    all_processed = []
    batch_url = None

    for file in files:
        # 1) save original
        raw_name, ext = os.path.splitext(file.filename)
        raw_path = os.path.join(upload_dir, file.filename)
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        # 2) generate unique variants
        seen = set()
        variants = []
        for i in range(1, count+1):
            while True:
                a = random.randint(-rotation, rotation)
                c = round(random.uniform(1-contrast, 1+contrast), 3)
                cp = round(random.uniform(0, crop), 3)
                key = (a, c, cp)
                if key not in seen:
                    seen.add(key)
                    break

            # open & process
            img = Image.open(raw_path)
            img = ImageEnhance.Contrast(img).enhance(c)
            img = img.rotate(a, expand=True)

            # crop‐and‐resize back to original
            w,h = img.size
            crop_px_w = int(w * cp)
            crop_px_h = int(h * cp)
            box = (
                crop_px_w, 
                crop_px_h, 
                w - crop_px_w, 
                h - crop_px_h
            )
            img = img.crop(box)
            img = img.resize((w, h), Image.LANCZOS)

            # name = original.1.jpg, original.2.jpg …
            variant = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, variant)
            img.save(out_path)
            variants.append(variant)
            all_processed.append({
                "image":        f"/uploads/{variant}",
                "download_link": f"/uploads/{variant}"
            })

        # 3) zip this batch
        zip_name = f"{raw_name}_batch.zip"
        zip_path = os.path.join(upload_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for fn in variants:
                zf.write(os.path.join(upload_dir, fn), arcname=fn)
        batch_url = f"/uploads/{zip_name}"

    return {"processed": all_processed, "batch": batch_url}
