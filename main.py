from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import moviepy.editor as mp
import os
import shutil

app = FastAPI()

# Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...), batch_size: int = Form(5), contrast_min: float = Form(-5.0), contrast_max: float = Form(5.0), flip: bool = Form(False)):
    filename = f"uploads/{file.filename}"

    # Save the uploaded file
    with open(filename, "wb") as f:
        f.write(await file.read())

    # Load the video using moviepy
    video = mp.VideoFileClip(filename)

    # Apply contrast adjustments (between the min and max provided)
    video = video.fx(mp.vfx.colorx, 1 + contrast_min / 100)  # Example of contrast adjustment (min)

    # If flip is selected, apply horizontal flip
    if flip:
        video = video.fx(mp.vfx.flip_horizontal)

    # Trim the video (example: trimming to first 10 seconds)
    video = video.subclip(0, 10)

    # Save the processed video
    processed_filename = f"uploads/processed_{file.filename}"
    video.write_videofile(processed_filename, codec="libx264", audio_codec="aac")

    # Return processed video URL
    return JSONResponse(content={"message": "Video processed", "processed_file": f"/uploads/{os.path.basename(processed_filename)}"})

# Health check
@app.head("/")
async def hc():
    return JSONResponse(status_code=200)
