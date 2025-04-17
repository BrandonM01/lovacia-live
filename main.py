from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from PIL import Image, ImageEnhance
import random

app = FastAPI()

# Serve HTML templates
templates = Jinja2Templates(directory="templates")
# Serve static files (for CSS/logo if needed)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route: Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route: Handle image uploads
@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    saved_files = []
    processed_files = []
    
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

        # Open the image using Pillow (PIL)
        image = Image.open(file_path)
        
        # Resize the image slightly
        new_size = tuple([int(i * 0.98) for i in image.size])  # Reduce size by 2%
        image = image.resize(new_size)

        # Rotate the image by a random degree
        angle = random.randint(-5, 5)  # Rotate by a random angle between -5 to 5 degrees
        image = image.rotate(angle)

        # Adjust contrast slightly
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(random.uniform(0.95, 1.05))  # Random contrast change between 95%-105%

        # Save the processed image with a modified name
        processed_filename = f"processed_{file.filename}"
        processed_path = os.path.join(upload_dir, processed_filename)
        image.save(processed_path)
        processed_files.append(processed_filename)

    return {"uploaded": saved_files, "processed": processed_files}
