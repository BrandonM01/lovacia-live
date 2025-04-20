FROM python:3.11-slim

WORKDIR /app

# install ffmpeg for moviepy
RUN apt-get update && apt-get install -y ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 10000
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port", "10000"]
