from fastapi import FastAPI, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os, zipfile, random, asyncio, json
from uuid import uuid4
from PIL import Image, ImageEnhance

app = FastAPI()
jobs: dict[str, dict] = {}

@app.head("/")
async def healthcheck():
    return Response(status_code=200)

# Prepare directories
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_images(
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


async def process_job(job_id, files, count, cmin, cmax, flip):
    UP = "uploads"
    job = jobs[job_id]

    min_c = 0.3
    min_r = 0.54
    min_cp = 0.01
    rot_range  = max(count * 0.2, min_r)
    crop_range = max(count * 0.001, min_cp)

    for file in files:
        name, ext = os.path.splitext(file.filename)
        ext_low = ext.lower()
        in_path = os.path.join(UP, file.filename)
        data    = await file.read()
        with open(in_path, "wb") as f:
            f.write(data)

        # Image variants
        if ext_low in {".jpg",".jpeg",".png",".gif"}:
            seen, variants = set(), []
            for i in range(1, count+1):
                while True:
                    a = random.uniform(-rot_range, rot_range)
                    if abs(a)<min_r: continue
                    c = random.uniform(cmin, cmax)
                    if abs(c)<min_c: continue
                    cp = random.uniform(min_cp, crop_range)
                    flip_flag = random.choice([True,False]) if flip else False
                    key = (round(a,2),round(c,2),round(cp,3),flip_flag)
                    if key not in seen:
                        seen.add(key)
                        break

                img = Image.open(in_path)
                img = ImageEnhance.Contrast(img).enhance(1 + c/100)
                img = img.rotate(a, expand=True)
                w,h = img.size
                cx,cy = int(w*cp), int(h*cp)
                img = img.crop((cx,cy,w-cx,h-cy)).resize((w,h), Image.LANCZOS)
                if flip_flag:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)

                var = f"{name}.{i}{ext}"
                out = os.path.join(UP, var)
                img.save(out)
                variants.append(var)

                job["items"].append({
                    "type": "image",
                    "thumb": f"/uploads/{var}",
                    "download": f"/uploads/{var}"
                })
                job["processed"] += 1

            # zip
            zipn = f"{name}_batch_{job_id}.zip"
            zipp = os.path.join(UP, zipn)
            with zipfile.ZipFile(zipp, "w") as zf:
                for v in variants:
                    zf.write(os.path.join(UP, v), arcname=v)
            job["batch_url"] = f"/uploads/{zipn}"

        # Video pass‑through batch
        elif ext_low in {".mp4",".mov",".avi",".mkv"}:
            for i in range(1, count+1):
                var = f"{name}.{i}{ext}"
                out = os.path.join(UP, var)
                with open(out, "wb") as f:
                    f.write(data)
                job["items"].append({
                    "type": "video",
                    "thumb": f"/uploads/{var}",
                    "download": f"/uploads/{var}"
                })
                job["processed"] += 1
            # no zip for videos

        else:
            continue


@app.get("/progress/{job_id}")
async def progress_events(job_id: str):
    if job_id not in jobs:
        return Response(status_code=404)
    async def gen():
        while True:
            j = jobs[job_id]
            yield f"data: {json.dumps({'processed':j['processed'],'total':j['total'],'batch_url':j['batch_url']})}\n\n"
            if j["batch_url"] is not None or j["processed"]>=j["total"]:
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(gen(), media_type="text/event-stream")


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    j = jobs.get(job_id)
    if not j:
        return JSONResponse(status_code=404, content={"error":"unknown job"})
    return {"items": j["items"], "batch_url": j["batch_url"]}
