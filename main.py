from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from image_processing import process_image
from video_processing import process_video

app = FastAPI()

# serve CSS/etc from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...)):
    # save upload
    tmp = "temp_image.jpg"
    with open(tmp, "wb") as f:
        f.write(await file.read())

    out = process_image(tmp, flip=True, contrast_min=-5.0, contrast_max=5.0)
    return FileResponse(out, media_type="image/jpeg", filename=out)

@app.post("/process-video/")
async def process_video_endpoint(file: UploadFile = File(...)):
    tmp = "temp_video.mp4"
    with open(tmp, "wb") as f:
        f.write(await file.read())

    out = process_video(tmp, trim_start=5, trim_end=10, flip=True)
    return FileResponse(out, media_type="video/mp4", filename=out)
