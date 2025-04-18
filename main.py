from fastapi import FastAPI, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, Response, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os, zipfile, random, asyncio, json
from uuid import uuid4
from PIL import Image, ImageEnhance

app = FastAPI()
jobs: dict[str, dict] = {}

# Health check for Render
@app.head("/")
async def hc():
    return Response(status_code=200)

# Prepare directories + mount
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
    jobs[job_id] = {"total": total, "processed": 0, "items": [], "batch_url": None}
    background_tasks.add_task(
        process_job, job_id, files, count, contrast_min, contrast_max, flip
    )
    return {"job_id": job_id}


async def process_job(job_id, files, count, contrast_min, contrast_max, flip):
    UP = "uploads"
    job = jobs[job_id]

    # thresholds
    min_contrast = 0.3
    min_rotation = 0.54
    min_crop     = 0.01
    rot_range    = max(count * 0.2, min_rotation)
    crop_range   = max(count * 0.001, min_crop)

    for file in files:
        name, ext = os.path.splitext(file.filename)
        raw_path  = os.path.join(UP, file.filename)
        data      = await file.read()
        with open(raw_path, "wb") as f:
            f.write(data)

        # If video, pass‐through
        if ext.lower() in {".mp4", ".mov", ".avi"}:
            job["items"].append({
                "image":  f"/uploads/{file.filename}",
                "download_link": f"/uploads/{file.filename}"
            })
            job["processed"] += 1
            continue

        # Otherwise generate variants
        seen, variants = set(), []
        for i in range(1, count+1):
            # pick unique
            while True:
                a = random.uniform(-rot_range, rot_range)
                if abs(a)<min_rotation: continue
                c = random.uniform(contrast_min, contrast_max)
                if abs(c)<min_contrast: continue
                cp = random.uniform(min_crop, crop_range)
                flip_flag = random.choice([True,False]) if flip else False
                key = (round(a,2),round(c,2),round(cp,3),flip_flag)
                if key not in seen:
                    seen.add(key)
                    break

            img = Image.open(raw_path)
            img = ImageEnhance.Contrast(img).enhance(1 + c/100)
            img = img.rotate(a, expand=True)
            w,h  = img.size
            cx,cy= int(w*cp), int(h*cp)
            img = img.crop((cx,cy,w-cx,h-cy)).resize((w,h), Image.LANCZOS)
            if flip_flag:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            out = f"{name}.{i}{ext}"
            pth = os.path.join(UP, out)
            img.save(pth)
            variants.append(out)

            url = f"/uploads/{out}"
            job["items"].append({"image": url, "download_link": url})
            job["processed"] += 1

        # zip batch        
        zname = f"{name}_batch_{job_id}.zip"
        zpth  = os.path.join(UP, zname)
        with zipfile.ZipFile(zpth, "w") as zf:
            for v in variants:
                zf.write(os.path.join(UP, v), arcname=v)
        job["batch_url"] = f"/uploads/{zname}"


@app.get("/progress/{job_id}")
async def progress_events(job_id: str):
    if job_id not in jobs:
        return Response(status_code=404)
    async def gen():
        while True:
            j = jobs[job_id]
            yield f"data: {json.dumps({'processed':j['processed'],'total':j['total'],'batch_url':j['batch_url']})}\n\n"
            if j["batch_url"]:
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    j = jobs.get(job_id)
    if not j:
        return JSONResponse(status_code=404, content={"error":"unknown job"})
    return {"items":j["items"], "batch_url":j["batch_url"]}
