from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from PIL import Image, ImageEnhance
import os, random, time, zipfile, json

app = FastAPI()

# ensure directories exist
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}

@app.post("/upload")
async def upload_stream(
    request: Request,
    files: list[UploadFile] = File(...),
    count: int = Form(5),
    contrast_min: float = Form(-5.0),
    contrast_max: float = Form(5.0),
    flip: bool = Form(False),
):
    """
    Streams Server‑Sent Events back to the client with:
     - progress: { done, total, percent, eta, last_image }
     - complete: { batch }
    """
    async def event_generator():
        start = time.time()
        total_variants = len(files) * count
        done = 0
        batch_url = None

        # process each file
        for file in files:
            raw_name, ext = os.path.splitext(file.filename)
            raw_path = os.path.join("uploads", file.filename)
            # save original
            with open(raw_path, "wb") as f:
                f.write(await file.read())

            variants = []
            seen = set()

            for i in range(1, count + 1):
                # abort if client disconnects
                if await request.is_disconnected():
                    return

                # pick a unique combo
                while True:
                    rot = random.uniform(-count*0.2, count*0.2)
                    con = random.uniform(contrast_min, contrast_max)
                    cp  = random.uniform(0, count*0.001)
                    flip_flag = flip and random.choice([True, False])
                    key = (round(rot,2), round(con,2), round(cp,3), flip_flag)
                    if key not in seen:
                        seen.add(key)
                        break

                # open & transform
                img = Image.open(raw_path)
                img = ImageEnhance.Contrast(img).enhance(1 + con/100)
                img = img.rotate(rot, expand=True)

                w,h = img.size
                cx = int(w*cp); cy = int(h*cp)
                img = img.crop((cx, cy, w-cx, h-cy))
                img = img.resize((w, h), Image.LANCZOS)
                if flip_flag:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)

                name = f"{raw_name}.{i}{ext}"
                out_path = os.path.join("uploads", name)
                img.save(out_path)
                variants.append(name)

                done += 1
                elapsed = time.time() - start
                per = elapsed/done
                eta = per*(total_variants-done)

                # send progress event
                yield {
                  "event": "progress",
                  "data": json.dumps({
                    "done": done,
                    "total": total_variants,
                    "percent": round(done/total_variants*100,1),
                    "eta": round(eta,1),
                    "last_image": f"/uploads/{name}"
                  })
                }

            # zip this batch
            zip_name = f"{raw_name}_batch.zip"
            zip_path = os.path.join("uploads", zip_name)
            with zipfile.ZipFile(zip_path, "w") as zf:
                for v in variants:
                    zf.write(os.path.join("uploads", v), arcname=v)
            batch_url = f"/uploads/{zip_name}"

        # final completion event
        yield {"event": "complete", "data": json.dumps({"batch": batch_url})}

    return EventSourceResponse(event_generator())

# serve your index.html + assets normally
templates_dir = "templates"
app.mount("/static", StaticFiles(directory="static"), name="static")
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=StreamingResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
