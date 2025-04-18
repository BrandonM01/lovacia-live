# Use a slim Python image
FROM python:3.11-slim

# Install ffmpeg for moviepy
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no‑cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
