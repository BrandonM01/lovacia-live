from fastapi import FastAPI, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os, zipfile, random, asyncio, json
from uuid import uuid4

from image_processing import process_image_variants
from video_processing import process_video_variants

app = FastAPI()

# In‑memory job store
jobs: dict[str, dict] = {}

# Health check
@app.head("/")
async def hc():
    return Response(status_code=200)

# Ensure dirs + mount static
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
    count: int              = Form(5),
    contrast_min: float     = Form(-5.0),
    contrast_max: float     = Form(5.0),
    flip: bool              = Form(False),
    trim_start: float       = Form(0.0),
    trim_end: float         = Form(0.0),
):
    job_id = str(uuid4())
    total  = len(files) * count
    jobs[job_id] = {"total": total, "processed": 0, "items": [], "batch_url": None}

    background_tasks.add_task(
        process_job, job_id, files, count,
        contrast_min, contrast_max, flip,
        trim_start, trim_end
    )
    return {"job_id": job_id}

async def process_job(job_id, files, count,
                      contrast_min, contrast_max, flip,
                      trim_start, trim_end):
    upload_dir = "uploads"
    job = jobs[job_id]

    for file in files:
        filename = file.filename
        raw_path = os.path.join(upload_dir, filename)
        contents = await file.read()
        with open(raw_path, "wb") as f:
            f.write(contents)

        # Branch on extension
        name, ext = os.path.splitext(filename)
        if ext.lower() in [".jpg",".jpeg",".png",".gif"]:
            variants = process_image_variants(
                raw_path, name, ext, count,
                contrast_min, contrast_max, flip
            )
        else:
            variants = process_video_variants(
                raw_path, name, ext, count,
                flip, trim_start, trim_end
            )

        # record URLs
        for v in variants:
            url = f"/uploads/{v}"
            job["items"].append({"url": url})
            job["processed"] += 1

        # zip them
        zip_name = f"{name}_batch_{job_id}.zip"
        zip_path = os.path.join(upload_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as z:
            for v in variants:
                z.write(os.path.join(upload_dir, v), arcname=v)
        job["batch_url"] = f"/uploads/{zip_name}"

@app.get("/progress/{job_id}")
async def progress_sse(job_id: str):
    if job_id not in jobs:
        return Response(status_code=404)
    async def streamer():
        while True:
            j = jobs[job_id]
            data = {"processed": j["processed"], "total": j["total"], "batch_url": j["batch_url"]}
            yield f"data: {json.dumps(data)}\n\n"
            if j["batch_url"]:
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(streamer(), media_type="text/event-stream")

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error":"unknown job"})
    return {"items": job["items"], "batch_url": job["batch_url"]}
