from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os, zipfile, random, asyncio, json
from uuid import uuid4
from PIL import Image, ImageEnhance
from moviepy.editor import VideoFileClip, vfx

app = FastAPI()

# simple in‑memory job store for progress
jobs: dict[str, dict] = {}

# Health check (Render)
@app.head("/")
async def hc():
    return Response(status_code=200)

# ensure & mount dirs
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(
    files: list[UploadFile] = File(...),
    count: int              = Form(5),
    contrast_min: float     = Form(-5.0),
    contrast_max: float     = Form(5.0),
    flip: bool              = Form(False),
):
    """
    Synchronous processing of images & videos.
    """
    upload_dir = "uploads"
    processed_items = []
    all_variants = []

    # thresholds
    min_contrast = 0.3    # user requested minimal contrast delta
    min_rot      = 0.54
    min_crop     = 0.01
    rot_range    = max(count * 0.2, min_rot)
    crop_range   = max(count * 0.001, min_crop)

    for file in files:
        raw_name, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        raw_path = os.path.join(upload_dir, file.filename)
        contents = await file.read()
        with open(raw_path, "wb") as f:
            f.write(contents)

        variants = []

        for i in range(1, count + 1):
            # pick unique params
            while True:
                a = random.uniform(-rot_range, rot_range)
                if abs(a) < min_rot: continue

                c = random.uniform(contrast_min, contrast_max)
                if abs(c) < min_contrast: continue

                cp = random.uniform(min_crop, crop_range)
                flip_flag = random.choice([True, False]) if flip else False

                key = (round(a,2), round(c,2), round(cp,3), flip_flag)
                if key not in variants:
                    variants.append(key)
                    break

            out_filename = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, out_filename)

            if ext in [".mp4", ".mov", ".avi"]:
                # video processing
                clip = VideoFileClip(raw_path)
                # contrast
                clip = clip.fx(vfx.colorx, 1 + c/100)
                # rotation
                clip = clip.rotate(a)
                # crop (crop margins cp on each side)
                w, h = clip.size
                x1, y1 = w*cp, h*cp
                clip = clip.crop(x1=x1, y1=y1, x2=w-x1, y2=h-y1)
                # flip
                if flip_flag:
                    clip = clip.fx(vfx.mirror_x)
                # write out
                clip.write_videofile(out_path, audio_codec="aac", verbose=False, logger=None)
                clip.close()
            else:
                # image processing
                img = Image.open(raw_path)
                img = ImageEnhance.Contrast(img).enhance(1 + c/100)
                img = img.rotate(a, expand=True)
                w, h = img.size
                cx, cy = int(w*cp), int(h*cp)
                img = img.crop((cx, cy, w-cx, h-cy))
                img = img.resize((w, h), Image.LANCZOS)
                if flip_flag:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img.save(out_path)

            url = f"/uploads/{out_filename}"
            processed_items.append({"image": url, "download_link": url})
            all_variants.append(out_filename)

    # zip them
    zip_name = f"batch_{uuid4().hex}.zip"
    zip_path = os.path.join(upload_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w") as zf:
        for fn in all_variants:
            zf.write(os.path.join(upload_dir, fn), arcname=fn)

    batch_url = f"/uploads/{zip_name}"
    return {"processed": processed_items, "batch": batch_url}
