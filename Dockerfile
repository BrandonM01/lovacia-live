FROM python:3.11-slim

# Install dependencies (including ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
