from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, zipfile, random
from uuid import uuid4
from PIL import Image, ImageEnhance
from moviepy.editor import VideoFileClip

app = FastAPI()

# Ensure upload+static dirs
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount them
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(
    files: list[UploadFile] = File(...),
    count: int = Form(5),
    contrast_min: float = Form(-5.0),
    contrast_max: float = Form(5.0),
    flip: bool = Form(False),
):
    upload_dir = "uploads"
    batch_id = uuid4().hex
    processed_items = []
    variants = []

    for file in files:
        raw_name, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        in_path = os.path.join(upload_dir, file.filename)
        # save original
        with open(in_path, "wb") as f:
            f.write(await file.read())

        seen = set()
        for i in range(1, count + 1):
            # pick unique transform
            while True:
                rot = random.uniform(-5 * count, 5 * count)
                con = random.uniform(contrast_min, contrast_max)
                crp = random.uniform(0.01, 0.05)
                flip_flag = random.choice([True, False]) if flip else False
                key = (round(rot,1), round(con,1), round(crp,2), flip_flag)
                if key not in seen:
                    seen.add(key)
                    break

            out_name = f"{raw_name}_{i}{ext}"
            out_path = os.path.join(upload_dir, out_name)

            if ext in (".mp4", ".mov", ".avi", ".mkv"):
                # video: re-encode and strip metadata
                clip = VideoFileClip(in_path)
                clip.write_videofile(
                    out_path,
                    codec="libx264",
                    audio_codec="aac",
                    ffmpeg_params=["-map_metadata", "-1"],
                    verbose=False, logger=None
                )
                clip.close()
            else:
                # image: enhance & rotate & crop & flip
                img = Image.open(in_path)
                img = ImageEnhance.Contrast(img).enhance(1 + con/100)
                img = img.rotate(rot, expand=True)
                w,h = img.size
                cx,cy = int(w*crp), int(h*crp)
                img = img.crop((cx,cy,w-cx,h-cy)).resize((w,h), Image.LANCZOS)
                if flip_flag:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                img.save(out_path)

            variants.append(out_name)
            url = f"/uploads/{out_name}"
            processed_items.append({"url": url, "filename": out_name})

    # zip up all variants
    zip_name = f"batch_{batch_id}.zip"
    zip_path = os.path.join(upload_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w") as zf:
        for fn in variants:
            zf.write(os.path.join(upload_dir, fn), arcname=fn)

    return {
        "items": processed_items,
        "zip_url": f"/uploads/{zip_name}"
    }
