from fastapi import FastAPI, UploadFile, File
from image_processing import process_image  # Import image processing helper
from video_processing import process_video  # Import video processing helper

app = FastAPI()

# Health check endpoint for service health monitoring
@app.head("/")
async def healthcheck():
    return {"status": "Service is running"}

# Endpoint to process uploaded images
@app.post("/process-image/")
async def process_image_endpoint(file: UploadFile = File(...)):
    # Save the uploaded image file
    with open("temp_image.jpg", "wb") as f:
        f.write(await file.read())

    # Process the image using the helper function from image_processing.py
    processed_image = process_image("temp_image.jpg", flip=True, contrast_min=-5.0, contrast_max=5.0)
    
    # Return the processed image filename
    return {"filename": processed_image}

# Endpoint to process uploaded videos
@app.post("/process-video/")
async def process_video_endpoint(file: UploadFile = File(...)):
    # Save the uploaded video file
    with open("temp_video.mp4", "wb") as f:
        f.write(await file.read())

    # Process the video using the helper function from video_processing.py
    processed_video = process_video("temp_video.mp4", trim_start=5, trim_end=10, flip=True)
    
    # Return the processed video filename
    return {"filename": processed_video}
