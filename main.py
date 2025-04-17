import os
import io
import zipfile
import uuid
import random
import time
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageEnhance

app = FastAPI()

# mount static & uploads
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

# in‑memory queues for each job
job_queues: dict[str, asyncio.Queue] = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_images(
    request: Request,
    background: BackgroundTasks,
    files: list[UploadFile]     = File(...),
    count: int                  = Form(5),
    contrast_min: float         = Form(-5.0),
    contrast_max: float         = Form(5.0),
    flip: bool                  = Form(False),
):
    job_id = str(uuid.uuid4())
    q = asyncio.Queue()
    job_queues[job_id] = q

    background.add_task(
        _process_job, job_id, files, count, contrast_min, contrast_max, flip
    )
    return {"job_id": job_id}

@app.get("/events/{job_id}")
async def events(job_id: str):
    """
    SSE endpoint. Yields events: 'progress', 'image', 'done'.
    """
    if job_id not in job_queues:
        return StreamingResponse(
            "event: error\ndata: Job not found\n\n",
            media_type="text/event-stream"
        )

    async def streamer():
        q = job_queues[job_id]
        while True:
            msg = await q.get()
            typ = msg["type"]
            data = msg["data"]
            payload = f"event: {typ}\ndata: {data}\n\n"
            yield payload
            if typ == "done":
                break
        # cleanup
        del job_queues[job_id]

    return StreamingResponse(streamer(), media_type="text/event-stream")

async def _process_job(job_id, files, count, cmin, cmax, flip):
    q = job_queues[job_id]
    upload_dir = "uploads"
    start = time.time()

    variants = []
    for idx, file in enumerate(files, 1):
        raw_name, ext = os.path.splitext(file.filename)
        raw_path = os.path.join(upload_dir, file.filename)
        # save original
        with open(raw_path, "wb") as f:
            f.write(await file.read())

        seen = set()
        for i in range(1, count+1):
            # pick unique transform
            while True:
                a = random.uniform(-count*0.2, count*0.2)
                if abs(a) < 0.54: continue
                c = random.uniform(cmin, cmax)
                if abs(c) < 0.3: continue
                cp = random.uniform(0, count*0.001)
                if cp < 0.01: continue
                flip_flag = random.choice([True,False]) if flip else False
                key = (round(a,2), round(c,2), round(cp,3), flip_flag)
                if key not in seen:
                    seen.add(key)
                    break

            img = Image.open(raw_path)
            img = ImageEnhance.Contrast(img).enhance(1 + c/100)
            img = img.rotate(a, expand=True)
            w,h = img.size
            cx, cy = int(w*cp), int(h*cp)
            img = img.crop((cx,cy,w-cx,h-cy)).resize((w,h), Image.LANCZOS)
            if flip_flag:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            variant = f"{raw_name}.{i}{ext}"
            out_path = os.path.join(upload_dir, variant)
            img.save(out_path)
            variants.append(variant)

            # SSE → image event
            ev = {
                "url": f"/uploads/{variant}",
                "download": f"/uploads/{variant}"
            }
            await q.put({"type":"image", "data": json.dumps(ev)})

            # SSE → progress event
            done = len(variants)
            total = len(files)*count
            elapsed = time.time() - start
            avg = elapsed/done
            eta = avg*(total - done)
            prog = {
                "done": done,
                "total": total,
                "percent": round(done/total*100,1),
                "eta": round(eta)
            }
            await q.put({"type":"progress", "data": json.dumps(prog)})

    # zip all variants
    batch_name = f"{raw_name}_batch.zip"
    batch_path = os.path.join(upload_dir, batch_name)
    with zipfile.ZipFile(batch_path, "w") as zf:
        for fn in variants:
            zf.write(os.path.join(upload_dir, fn), arcname=fn)

    # SSE → done event
    done_data = {"batch": f"/uploads/{batch_name}"}
    await q.put({"type":"done", "data": json.dumps(done_data)})
