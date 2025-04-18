from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, zipfile, random, uuid
from PIL import Image, ImageEnhance
from moviepy.editor import VideoFileClip, vfx

app = FastAPI()

# health‑check for Render
@app.head("/")
async def hc():
    return Response(status_code=200)

# make + mount dirs
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
    files: list[UploadFile]          = File(...),
    count: int                       = Form(5),
    contrast_min: float              = Form(-5.0),
    contrast_max: float              = Form(5.0),
    flip: bool                       = Form(False),
):
    upload_dir = "uploads"
    all_processed = []
    # thresholds
    min_contrast = 0.3
    min_rotation = 0.54
    min_crop     = 0.01
    rot_range    = max(count * 0.2, min_rotation)
    crop_range   = max(count * 0.001, min_crop)

    for file in files:
        raw_name, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        raw_path = os.path.join(upload_dir, file.filename)
        # save original
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        seen = set()
        variants = []

        for i in range(1, count + 1):
            # pick unique combo
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

            out_name = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, out_name)

            # IMAGE
            if ext in (".jpg", ".jpeg", ".png"):
                img = Image.open(raw_path)
                img = ImageEnhance.Contrast(img).enhance(1 + c/100)
                img = img.rotate(a, expand=True)
                w,h = img.size
                cx,cy = int(w*cp), int(h*cp)
                img = img.crop((cx,cy,w-cx,h-cy)).resize((w,h), Image.LANCZOS)
                if flip_flag:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img.save(out_path)

            # VIDEO
            elif ext in (".mp4", ".mov", ".avi", ".mkv"):
                clip = VideoFileClip(raw_path).without_audio()
                clip = clip.fx(vfx.colorx, 1 + c/100)
                if abs(a) > 0.1:
                    clip = clip.rotate(a)
                w,h = clip.size
                l,t = int(w*cp), int(h*cp)
                clip = clip.crop(x1=l,y1=t,x2=w-l,y2=h-t).resize((w,h))
                if flip_flag:
                    clip = clip.fx(vfx.mirror_x)
                clip.write_videofile(out_path, audio=False, verbose=False, logger=None)
                clip.close()

            else:
                # skip unsupported
                continue

            url = f"/uploads/{out_name}"
            all_processed.append({"image": url, "download_link": url})

        # zip this batch
        zip_name = f"{raw_name}_batch.zip"
        zip_path = os.path.join(upload_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for fn in [v["download_link"].split("/")[-1] for v in all_processed if v["download_link"].startswith(f"/uploads/{raw_name}.")]:
                zf.write(os.path.join(upload_dir, fn), arcname=fn)

        batch_url = f"/uploads/{zip_name}"

    return {"processed": all_processed, "batch": batch_url}
