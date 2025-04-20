# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# install ffmpeg for video support
RUN apt-get update && apt-get install -y ffmpeg

# install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy your code
COPY . /app

# expose port
EXPOSE 10000

# run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
