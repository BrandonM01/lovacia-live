# main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from image_processing import process_image
from video_processing import process_video

import os, uuid, json, zipfile, asyncio

app = FastAPI()

# In‑memory job store
jobs: dict[str, dict] = {}

# Health‑check
@app.head("/")
async def hc():
    return JSONResponse(status_code=200, content={"status": "ok"})

# Serve static files and templates
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    count: int = 5,
    contrast_min: float = -5.0,
    contrast_max: float = 5.0,
    flip: bool = False,
):
    job_id = str(uuid.uuid4())
    total = len(files) * count
    jobs[job_id] = {"total": total, "processed": 0, "items": [], "batch_url": None}
    background_tasks.add_task(process_job, job_id, files, count, contrast_min, contrast_max, flip)
    return {"job_id": job_id}

async def process_job(job_id, files, count, contrast_min, contrast_max, flip):
    job = jobs[job_id]
    variants = []

    for file in files:
        raw_name, ext = os.path.splitext(file.filename)
        raw_path = os.path.join("uploads", file.filename)
        contents = await file.read()
        with open(raw_path, "wb") as f:
            f.write(contents)

        # Images
        if ext.lower() in (".jpg", ".jpeg", ".png", ".gif"):
            for i in range(count):
                out = process_image(
                    raw_path,
                    flip=flip,
                    contrast_min=contrast_min,
                    contrast_max=contrast_max,
                    suffix=f".img{i+1}"
                )
                job["items"].append({"image": out})
                job["processed"] += 1

        # Videos
        elif ext.lower() in (".mp4", ".mov", ".avi"):
            for i in range(count):
                out = process_video(
                    raw_path,
                    trim_start=0,
                    trim_end=None,
                    flip=flip,
                    suffix=f".vid{i+1}"
                )
                job["items"].append({"video": out})
                job["processed"] += 1

    # Once done, zip everything
    zip_name = f"batch_{job_id}.zip"
    zip_path = os.path.join("uploads", zip_name)
    with zipfile.ZipFile(zip_path, "w") as zf:
        for item in job["items"]:
            fn = item.get("image") or item.get("video")
            zf.write(os.path.join("uploads", fn), arcname=fn)
    job["batch_url"] = f"/uploads/{zip_name}"

@app.get("/progress/{job_id}")
async def progress(job_id: str):
    if job_id not in jobs:
        return JSONResponse(status_code=404, content={"error": "unknown job"})
    async def gen():
        while True:
            j = jobs[job_id]
            yield f"data: {json.dumps({'processed': j['processed'], 'total': j['total'], 'batch_url': j['batch_url']})}\n\n"
            if j["batch_url"]:
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/results/{job_id}")
async def results(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "unknown job"})
    return {"items": job["items"], "batch_url": job["batch_url"]}
