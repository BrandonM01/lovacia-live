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

# ensure + mount uploads  
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
        raw_path = os.path.join(upload_dir, file.filename)  
        with open(raw_path, "wb") as f:  
            f.write(await file.read())  

        # generate N unique variations  
        seen = set()  
        for _ in range(count):  
            # pick random params until we hit a new combo  
            while True:  
                angle    = random.randint(-5, 5)                        # -5° to +5°  
                scale    = round(random.uniform(0.95, 1.05), 3)          # 0.95–1.05  
                contrast = round(random.uniform(0.95, 1.05), 3)          # 0.95–1.05  
                key = (angle, scale, contrast)  
                if key not in seen:  
                    seen.add(key)  
                    break  

            # process with those exact params  
            out_path = process_image(raw_path, angle, scale, contrast)  
            fn = os.path.basename(out_path)  
            processed_files.append({  
                "image":        f"/uploads/{fn}",  
                "download_link": f"/uploads/{fn}"  
            })  

    return {"processed": processed_files}  

def process_image(file_path: str, rotation: int, scale: float, contrast: float) -> str:  
    img = Image.open(file_path)  

    # 1) Contrast  
    enhancer = ImageEnhance.Contrast(img)  
    img = enhancer.enhance(contrast)  

    # 2) Rotation  
    img = img.rotate(rotation, expand=True)  

    # 3) Scale  
    if scale != 1.0:  
        w, h = img.size  
        img = img.resize((int(w * scale), int(h * scale)))  

    # save under uploads/ with a unique name  
    fn = f"proc_{rotation}_{int(scale*1000)}_{int(contrast*1000)}_{random.randint(1000,9999)}.jpg"  
    out_path = os.path.join("uploads", fn)  
    img.save(out_path)  

    return out_path  
