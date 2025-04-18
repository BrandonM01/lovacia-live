# Use the slim Python image
FROM python:3.11-slim

# Install ffmpeg so MoviePy can do video processing
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and run Uvicorn
EXPOSE 10000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
