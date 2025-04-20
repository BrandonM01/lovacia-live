from fastapi import FastAPI, UploadFile, File
from image_processing import process_image
from video_processing import process_video

app = FastAPI()

@app.head("/")
async def healthcheck():
    return {"status": "ok"}

@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...)):
    # 1) save upload
    with open("temp_image.jpg", "wb") as f:
        f.write(await file.read())
    # 2) process
    out = process_image("temp_image.jpg", flip=True)
    return {"filename": out}

@app.post("/process-video/")
async def process_video_endpoint(file: UploadFile = File(...)):
    # 1) save upload
    with open("temp_video.mp4", "wb") as f:
        f.write(await file.read())
    # 2) process
    out = process_video("temp_video.mp4", trim_start=5, trim_end=10, flip=True)
    return {"filename": out}
