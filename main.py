from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from PIL import Image, ImageEnhance
import random

app = FastAPI()

# templates + static
templates = Jinja2Templates(directory="templates")
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ensure + mount uploads folder
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_images(
    files: list[UploadFile] = File(...),
    count: int = Form(1)
):
    upload_dir = "uploads"
    processed_files = []

    for file in files:
        # save original
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # generate `count` processed variants
        for _ in range(count):
            processed_path = process_image(file_path)
            fn = os.path.basename(processed_path)
            processed_files.append({
                "image": f"/uploads/{fn}",
                "download_link": f"/uploads/{fn}"
            })

    return {"processed": processed_files}

def process_image(file_path: str) -> str:
    try:
        img = Image.open(file_path)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)

        # random filename & save into uploads/
        processed_fn = f"proc_{random.randint(1000,9999)}.jpg"
        out_path = os.path.join("uploads", processed_fn)
        img.save(out_path)
        return out_path

    except Exception as e:
        print("Processing error:", e)
        return file_path
