from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, zipfile, random, asyncio, json
from uuid import uuid4
from PIL import Image, ImageEnhance

app = FastAPI()

# healthcheck for Render
@app.head("/")
async def healthcheck():
    return Response(status_code=200)

# ensure + mount folders
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
    request: Request,
    files: list[UploadFile]     = File(...),
    count: int                  = Form(5),
    contrast_min: float         = Form(-5.0),
    contrast_max: float         = Form(5.0),
    flip: bool                  = Form(False),
):
    """Process each file: if image, apply subtle variations; if video, just save."""
    upload_dir = "uploads"
    processed = []

    # thresholds
    min_contrast = 0.3
    min_rotation = 0.54
    min_crop     = 0.01
    rot_range    = max(count * 0.2, min_rotation)
    crop_range   = max(count * 0.001, min_crop)

    for file in files:
        raw_name, ext = os.path.splitext(file.filename)
        ext_low = ext.lower()
        raw_path = os.path.join(upload_dir, file.filename)

        # read & write original to uploads/
        contents = await file.read()
        with open(raw_path, "wb") as f:
            f.write(contents)

        # decide branch by extension
        if ext_low in [".jpg", ".jpeg", ".png", ".gif"]:
            # image variants
            seen = set()
            for i in range(1, count + 1):
                # pick unique params
                while True:
                    a = random.uniform(-rot_range, rot_range)
                    if abs(a) < min_rotation: continue

                    c = random.uniform(contrast_min, contrast_max)
                    if abs(c) < min_contrast: continue

                    cp = random.uniform(min_crop, crop_range)
                    flip_flag = random.choice([True, False]) if flip else False

                    key = (round(a,2), round(c,2), round(cp,3), flip_flag)
                    if key not in seen:
                        seen.add(key)
                        break

                # apply transforms
                img = Image.open(raw_path)
                img = ImageEnhance.Contrast(img).enhance(1 + c/100)
                img = img.rotate(a, expand=True)
                w, h = img.size
                cx, cy = int(w*cp), int(h*cp)
                img = img.crop((cx, cy, w-cx, h-cy))
                img = img.resize((w, h), Image.LANCZOS)
                if flip_flag:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)

                variant = f"{raw_name}.{i}{ext}"
                out_path = os.path.join(upload_dir, variant)
                img.save(out_path)

                processed.append({
                    "type": "image",
                    "thumb": f"/uploads/{variant}",
                    "download": f"/uploads/{variant}"
                })

            # zip up the image variants
            zip_name = f"{raw_name}_batch_{uuid4().hex}.zip"
            zip_path = os.path.join(upload_dir, zip_name)
            with zipfile.ZipFile(zip_path, "w") as zf:
                for i in range(1, count+1):
                    fn = f"{raw_name}.{i}{ext}"
                    zf.write(os.path.join(upload_dir, fn), arcname=fn)
            batch_url = f"/uploads/{zip_name}"

        elif ext_low in [".mp4", ".mov", ".avi", ".mkv"]:
            # just pass through the video
            processed.append({
                "type": "video",
                "thumb": f"/uploads/{file.filename}",
                "download": f"/uploads/{file.filename}"
            })
            batch_url = None

        else:
            # skip unknown types
            continue

    return JSONResponse({"processed": processed, "batch": batch_url})
