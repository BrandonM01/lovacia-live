# Dockerfile

# 1) Use the official Python 3.11 slim image
FROM python:3.11-slim

# 2) Install ffmpeg (MoviePy needs the ffmpeg binary) and clean up apt cache
RUN apt-get update \
 && apt-get install -y ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 3) Set working directory
WORKDIR /app

# 4) Copy only requirements first (for better layer caching)
COPY requirements.txt .

# 5) Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy the rest of your application code
COPY . .

# 7) Expose the port your app listens on
EXPOSE 10000

# 8) Launch Uvicorn using python3 to guarantee the right interpreter
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
