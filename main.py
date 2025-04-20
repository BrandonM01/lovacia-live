from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from image_processing import process_image
from video_processing import process_video

app = FastAPI()

# 1) Mount /static → ./static
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2) Set up Jinja2Templates to serve index.html
templates = Jinja2Templates(directory="templates")


# Health‐check for Uptime monitors (HEAD and GET)
@app.head("/")
async def _healthcheck_head():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 3) Image endpoint
@app.post("/process-image/")
async def process_image_endpoint(
    file: UploadFile = File(...),
    count: int = Form(5),
    contrast_min: float = Form(-5.0),
    contrast_max: float = Form(5.0),
    flip: bool = Form(False),
):
    in_path = f"/tmp/{file.filename}"
    with open(in_path, "wb") as f:
        f.write(await file.read())

    out_path = process_image(
        input_path=in_path,
        flip=flip,
        contrast_min=contrast_min,
        contrast_max=contrast_max,
        count=count,
    )
    return FileResponse(out_path, media_type="image/jpeg", filename=out_path.split("/")[-1])


# 4) Video endpoint
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
