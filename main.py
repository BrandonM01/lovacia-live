from fastapi import FastAPI, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, Response, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os, zipfile, random, asyncio, json
from uuid import uuid4
from PIL import Image, ImageEnhance
from moviepy.editor import VideoFileClip  # ← now available

app = FastAPI()

# In‑memory job store
jobs: dict[str, dict] = {}

# Health check
@app.head("/")
async def hc():
    return Response(status_code=200)

# Ensure + mount static & uploads
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
):
    job_id = str(uuid4())
    total  = len(files) * count
    jobs[job_id] = {
        "total": total,
        "processed": 0,
        "items": [],
        "batch_url": None
    }
    background_tasks.add_task(
        process_job, job_id, files, count, contrast_min, contrast_max, flip
    )
    return {"job_id": job_id}


async def process_job(job_id, files, count, contrast_min, contrast_max, flip):
    upload_dir = "uploads"
    job = jobs[job_id]

    # minimum thresholds
    min_contrast = 0.3
    min_rotation = 0.54
    min_crop     = 0.01

    rot_range  = max(count * 0.2, min_rotation)
    crop_range = max(count * 0.001, min_crop)

    for file in files:
        raw_name, ext = os.path.splitext(file.filename)
        raw_path = os.path.join(upload_dir, file.filename)
        contents = await file.read()
        with open(raw_path, "wb") as f:
            f.write(contents)

        # If it's a video, just copy it through (or you could use moviepy to re‑encode metadata)
        if ext.lower() in {".mp4", ".mov", ".avi"}:
            job["items"].append({
                "image": f"/uploads/{file.filename}",
                "download_link": f"/uploads/{file.filename}"
            })
            job["processed"] += 1
            continue

        # Otherwise treat as an image
        seen = set()
        variants = []
        for i in range(1, count + 1):
            # pick unique params
            while True:
                a = random.uniform(-rot_range, rot_range)
                if abs(a) < min_rotation: continue

                c = random.uniform(contrast_min, contrast_max)
                if abs(c) < min_contrast: continue

                cp = random.uniform(min_crop, crop_range)
                flip_flag = random.choice([True, False]) if flip else False

                key = (round(a,2), round(c,2), round(cp,3), flip_flag)
                if key not in seen:
                    seen.add(key)
                    break

            # apply transforms
            img = Image.open(raw_path)
            img = ImageEnhance.Contrast(img).enhance(1 + c/100)
            img = img.rotate(a, expand=True)
            w, h = img.size
            cx, cy = int(w*cp), int(h*cp)
            img = img.crop((cx, cy, w-cx, h-cy))
            img = img.resize((w, h), Image.LANCZOS)
            if flip_flag:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            variant = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, variant)
            img.save(out_path)
            variants.append(variant)

            url = f"/uploads/{variant}"
            job["items"].append({"image": url, "download_link": url})
            job["processed"] += 1

        # zip batch
        zip_name = f"{raw_name}_batch_{job_id}.zip"
        zip_path = os.path.join(upload_dir, zip_name)
        with zipfile.ZipFile(zip_path, "w") as zf:
            for fn in variants:
                zf.write(os.path.join(upload_dir, fn), arcname=fn)
        job["batch_url"] = f"/uploads/{zip_name}"


@app.get("/progress/{job_id}")
async def progress_events(job_id: str):
    if job_id not in jobs:
        return Response(status_code=404)
    async def generator():
        while True:
            job = jobs[job_id]
            data = {
                "processed": job["processed"],
                "total": job["total"],
                "batch_url": job["batch_url"]
            }
            yield f"data: {json.dumps(data)}\n\n"
            if job["batch_url"] is not None:
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(generator(), media_type="text/event-stream")


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "unknown job"})
    return {"items": job["items"], "batch_url": job["batch_url"]}
