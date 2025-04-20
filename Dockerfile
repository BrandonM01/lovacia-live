# Use the official Python base image
FROM python:3.11-slim

# Install ffmpeg system binary (and any OS deps you need for PIL)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      libjpeg62-turbo-dev \
      && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port and launch Uvicorn
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
