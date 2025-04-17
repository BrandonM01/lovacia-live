from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, zipfile, random
from PIL import Image, ImageEnhance

app = FastAPI()

# health-check for Render
@app.head("/")
async def healthcheck():
    return Response(status_code=200)

templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static")), name="static")

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_images(
    request: Request,
    files: list[UploadFile] = File(...),
    count: int = Form(5),
    contrast_min: float = Form(-5.0),
    contrast_max: float = Form(5.0),
    flip: bool = Form(False),
):
    upload_dir = "uploads"
    all_processed = []

    # minimum thresholds
    min_contrast = 0.1
    min_rotation = 0.54
    min_crop = 0.01

    # dynamic ranges
    rot_range = max(count * 0.2, min_rotation)
    crop_range = max(count * 0.001, min_crop)

    for file in files:
        if await request.is_disconnected():
            break

        raw_name, ext = os.path.splitext(file.filename)
        raw_path = os.path.join(upload_dir, file.filename)
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        seen = set()
        variants = []

        for i in range(1, count + 1):
            if await request.is_disconnected():
                break

            # pick unique params
            while True:
                a = random.uniform(-rot_range, rot_range)
                if abs(a) < min_rotation: continue
                c = random.uniform(contrast_min, contrast_max)
                if abs(c) < min_contrast: continue
                cp = random.uniform(0, crop_range)
                if cp < min_crop: continue
                flip_flag = random.choice([True, False]) if flip else False
                key = (round(a,2), round(c,2), round(cp,3), flip_flag)
                if key not in seen:
                    seen.add(key)
                    break

            # apply
            img = Image.open(raw_path)
            img = ImageEnhance.Contrast(img).enhance(1 + c/100)
            img = img.rotate(a, expand=True)
            w,h = img.size
            cx, cy = int(w*cp), int(h*cp)
            img = img.crop((cx, cy, w-cx, h-cy))
            img = img.resize((w,h), Image.LANCZOS)
            if flip_flag:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            variant = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, variant)
            img.save(out_path)
            variants.append(variant)
            all_processed.append({
                "image": f"/uploads/{variant}",
                "download_link": f"/uploads/{variant}"
            })

        # zip and batch URL
        zip_name = f"{raw_name}_batch.zip"
        zip_path = os.path.join(upload_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for fn in variants:
                zf.write(os.path.join(upload_dir, fn), arcname=fn)
        batch_url = f"/uploads/{zip_name}"

    return {"processed": all_processed, "batch": batch_url}
