@app.post("/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    saved_files = []
    processed_files = []
    
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

        # Process the image (resize, rotate, contrast)
        image = Image.open(file_path)
        new_size = tuple([int(i * 0.98) for i in image.size])  # Reduce size by 2%
        image = image.resize(new_size)

        angle = random.randint(-5, 5)
        image = image.rotate(angle)

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(random.uniform(0.95, 1.05))  # Random contrast change

        processed_filename = f"processed_{file.filename}"
        processed_path = os.path.join(upload_dir, processed_filename)
        image.save(processed_path)
        processed_files.append(f"/uploads/{processed_filename}")  # Store path for preview

    return {"uploaded": saved_files, "processed": processed_files}
