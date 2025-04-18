# use a slim Python base
FROM python:3.11-slim

# install ffmpeg for video processing
RUN apt-get update && apt-get install -y ffmpeg

# set working dir
WORKDIR /app

# install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy our app
COPY . .

# launch
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
