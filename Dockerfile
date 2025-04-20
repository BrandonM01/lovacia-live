# 1. Base image
FROM python:3.11-slim

# 2. Install system deps for Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libjpeg62-turbo-dev && \
    rm -rf /var/lib/apt/lists/*

# 3. Set workdir
WORKDIR /app

# 4. Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Expose & launch
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
