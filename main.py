from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from image_processing import process_image
from video_processing import process_video
import os

app = FastAPI()

# Healthcheck
@app.get("/")
async def healthcheck():
    return {"status": "running"}

# Image endpoint
@app.post("/process-image/")
async def process_image_endpoint(
    file: UploadFile = File(...),
    flip: bool = Query(False),
    contrast_min: float = Query(-5.0),
    contrast_max: float = Query(5.0),
):
    # save upload
    tmp = "temp.jpg"
    with open(tmp, "wb") as f:
        f.write(await file.read())

    try:
        out = process_image(tmp, flip=flip, contrast_min=contrast_min, contrast_max=contrast_max)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(out, media_type="image/jpeg", filename=os.path.basename(out))

# Video endpoint
@app.post("/process-video/")
async def process_video_endpoint(
    file: UploadFile = File(...),
    trim_start: float = Query(0.0),
    trim_end: float | None = Query(None),
    flip: bool = Query(False),
):
    tmp = "temp.mp4"
    with open(tmp, "wb") as f:
        f.write(await file.read())

    try:
        out = process_video(tmp, trim_start=trim_start, trim_end=trim_end, flip=flip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(out, media_type="video/mp4", filename=os.path.basename(out))
