from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from image_processing import process_image
from video_processing import process_video

app = FastAPI()

@app.head("/")
async def healthcheck():
    return {"status": "ok"}

@app.post("/process-image/")
async def process_image_endpoint(
    file: UploadFile = File(...),
    count: int = Form(5),
    contrast_min: float = Form(-5.0),
    contrast_max: float = Form(5.0),
    flip: bool = Form(False),
):
    # save upload
    in_path = f"/tmp/{file.filename}"
    with open(in_path, "wb") as f:
        f.write(await file.read())
    # process
    out_path = process_image(
        input_path=in_path,
        flip=flip,
        contrast_min=contrast_min,
        contrast_max=contrast_max,
        count=count,
    )
    return FileResponse(out_path, media_type="image/jpeg", filename=out_path.split("/")[-1])

@app.post("/process-video/")
async def process_video_endpoint(
    file: UploadFile = File(...),
    trim_start: float = Form(0.0),
    trim_end: float = Form(0.0),
    flip: bool = Form(False),
):
    in_path = f"/tmp/{file.filename}"
    with open(in_path, "wb") as f:
        f.write(await file.read())
    out_path = process_video(
        input_path=in_path,
        trim_start=trim_start,
        trim_end=trim_end,
        flip=flip,
    )
    return FileResponse(out_path, media_type="video/mp4", filename=out_path.split("/")[-1])
