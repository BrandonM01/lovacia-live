# Dockerfile

# 1. Base image
FROM python:3.11-slim

# 2. Install OS deps (including ffmpeg)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 3. Set working dir
WORKDIR /app

# 4. Copy your code & install Python deps
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expose port & run
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
