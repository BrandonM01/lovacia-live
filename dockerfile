# Dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /app

# Copy code
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Expose and run
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
