from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os, zipfile, random
from PIL import Image, ImageEnhance

app = FastAPI()

# Templates + static
templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure + mount uploads/
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_images(
    files: list[UploadFile] = File(...),
    count: int = Form(1),
    contrast: float = Form(1.0),
    rotation: int = Form(0),
    scale: float = Form(1.0)
):
    upload_dir = "uploads"
    all_processed = []
    batch_url = None

    for file in files:
        # 1) Save original
        raw_name, ext = os.path.splitext(file.filename)
        raw_path = os.path.join(upload_dir, file.filename)
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        # 2) Generate variants
        seen = set()
        processed_names = []
        for i in range(1, count+1):
            # ensure unique random params
            while True:
                a = random.randint(-rotation, rotation)
                s = round(random.uniform(1-scale, 1+scale), 3)
                c = round(random.uniform(1-contrast, 1+contrast), 3)
                key = (a, s, c)
                if key not in seen:
                    seen.add(key)
                    break

            # process
            img = Image.open(raw_path)
            img = ImageEnhance.Contrast(img).enhance(c)
            img = img.rotate(a, expand=True)
            if s != 1.0:
                w,h = img.size
                img = img.resize((int(w*s), int(h*s)))

            # name variant: original.1.jpg, original.2.jpg, …
            variant = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, variant)
            img.save(out_path)
            processed_names.append(variant)
            all_processed.append({
                "image": f"/uploads/{variant}",
                "download_link": f"/uploads/{variant}"
            })

        # 3) Zip those variants
        zip_name = f"{raw_name}_batch.zip"
        zip_path = os.path.join(upload_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for fn in processed_names:
                zf.write(os.path.join(upload_dir, fn), arcname=fn)
        batch_url = f"/uploads/{zip_name}"

    return {"processed": all_processed, "batch": batch_url}
