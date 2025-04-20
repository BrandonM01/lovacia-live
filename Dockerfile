# 1) Base image with Python
FROM python:3.11-slim

# 2) Install ffmpeg system dependency (needed by moviepy & imageio‑ffmpeg)
RUN apt-get update \
 && apt-get install -y ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 3) Copy & install Python requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy your application code
COPY . .

# 5) Expose the port FastAPI/Uvicorn will listen on
EXPOSE 10000

# 6) Start your FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
